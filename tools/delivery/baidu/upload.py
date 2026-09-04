#!/usr/bin/env python3
"""Optional Baidu Netdisk upload CLI (xpan precreate → slice → create).

Tokens are read from AMRH_BAIDU_* env vars or AMRH_BAIDU_CREDENTIALS_FILE.
Nothing in this module prints credential values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

SLICE_BYTES = 4 * 1024 * 1024
PRECREATE_URL = "https://pan.baidu.com/rest/2.0/xpan/file"
PCS_URL = "https://d.pcs.baidu.com/rest/2.0/pcs/superfile2"
CREATE_URL = "https://pan.baidu.com/rest/2.0/xpan/file"


class CredentialError(RuntimeError):
    """Missing or unsafe credentials."""


@dataclass(frozen=True)
class Credentials:
    access_token: str
    refresh_token: str | None
    app_key: str | None
    secret_key: str | None
    app_name: str


def _load_secret_file(path: Path) -> dict:
    if not path.is_file():
        raise CredentialError("credentials file is missing")
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise CredentialError(f"credentials file mode is {mode:04o}; chmod 600")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CredentialError("credentials file must be a JSON object")
    return value


def load_credentials(
    environ: dict[str, str] | None = None,
    credentials_file: Path | None = None,
) -> Credentials:
    env = os.environ if environ is None else environ
    file_path = credentials_file
    if file_path is None and env.get("AMRH_BAIDU_CREDENTIALS_FILE"):
        file_path = Path(env["AMRH_BAIDU_CREDENTIALS_FILE"]).expanduser()
    file_values = _load_secret_file(file_path) if file_path else {}
    token = env.get("AMRH_BAIDU_ACCESS_TOKEN") or file_values.get("access_token")
    if not token:
        raise CredentialError(
            "set AMRH_BAIDU_ACCESS_TOKEN or AMRH_BAIDU_CREDENTIALS_FILE"
        )
    return Credentials(
        access_token=str(token),
        refresh_token=env.get("AMRH_BAIDU_REFRESH_TOKEN") or file_values.get("refresh_token"),
        app_key=env.get("AMRH_BAIDU_APP_KEY") or file_values.get("app_key"),
        secret_key=env.get("AMRH_BAIDU_SECRET_KEY") or file_values.get("secret_key"),
        app_name=str(
            env.get("AMRH_BAIDU_APP_NAME")
            or file_values.get("app_name")
            or "amrh"
        ),
    )


def md5_blocks(path: Path, slice_bytes: int = SLICE_BYTES) -> list[str]:
    digests: list[str] = []
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(slice_bytes)
            if not chunk:
                break
            digests.append(hashlib.md5(chunk).hexdigest())
    if not digests:
        digests.append(hashlib.md5(b"").hexdigest())
    return digests


def normalize_remote(remote: str, app_name: str) -> str:
    if remote.startswith("/apps/"):
        return remote
    trimmed = remote.lstrip("/")
    return f"/apps/{app_name}/{trimmed}"


def plan_upload(local: Path, remote: str, credentials: Credentials | None) -> dict:
    blocks = md5_blocks(local) if local.is_file() else []
    app_name = credentials.app_name if credentials else "amrh"
    return {
        "local": local.name,
        "local_exists": local.is_file(),
        "size": local.stat().st_size if local.is_file() else 0,
        "remote": normalize_remote(remote, app_name),
        "block_count": len(blocks),
        "steps": ["precreate", "superfile2", "create"],
        "has_token": credentials is not None,
    }


def _post_form(url: str, params: dict[str, str], data: dict[str, str]) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    encoded = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(full, data=encoded, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def upload(local: Path, remote: str, credentials: Credentials) -> dict:
    if not local.is_file():
        raise FileNotFoundError(local)
    dest = normalize_remote(remote, credentials.app_name)
    blocks = md5_blocks(local)
    precreate = _post_form(
        PRECREATE_URL,
        {"method": "precreate", "access_token": credentials.access_token},
        {
            "path": dest,
            "size": str(local.stat().st_size),
            "isdir": "0",
            "autoinit": "1",
            "block_list": json.dumps(blocks),
        },
    )
    upload_id = precreate.get("uploadid")
    if not upload_id:
        raise RuntimeError("precreate did not return uploadid")
    with local.open("rb") as handle:
        for index, digest in enumerate(blocks):
            chunk = handle.read(SLICE_BYTES)
            query = urllib.parse.urlencode(
                {
                    "method": "upload",
                    "access_token": credentials.access_token,
                    "type": "tmpfile",
                    "path": dest,
                    "uploadid": upload_id,
                    "partseq": str(index),
                }
            )
            request = urllib.request.Request(
                PCS_URL + "?" + query,
                data=chunk,
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
            if body.get("md5") and body["md5"] != digest:
                raise RuntimeError("slice md5 mismatch")
    created = _post_form(
        CREATE_URL,
        {"method": "create", "access_token": credentials.access_token},
        {
            "path": dest,
            "size": str(local.stat().st_size),
            "isdir": "0",
            "uploadid": upload_id,
            "block_list": json.dumps(blocks),
        },
    )
    return {"remote": dest, "fs_id": created.get("fs_id"), "size": created.get("size")}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/cli.py baidu-upload",
        description=(
            "可选：把成片上传到百度网盘（只上传，不下载、不删、不改分享）。"
            "凭证来自仓库外的 AMRH_BAIDU_CREDENTIALS_FILE（0600 JSON）"
            "或 AMRH_BAIDU_ACCESS_TOKEN。从不打印密钥。"
        ),
        epilog=(
            "空跑：python3 tools/cli.py baidu-upload -- --dry-run "
            "--local README.md --remote /apps/amrh/readme.md\n"
            "实际上传：先 export AMRH_BAIDU_CREDENTIALS_FILE，再去掉 --dry-run。"
        ),
    )
    parser.add_argument(
        "--local",
        required=True,
        type=Path,
        help="本机文件（成片 mp4，或空跑时任意小文件）",
    )
    parser.add_argument(
        "--remote",
        required=True,
        help="网盘路径；不以 /apps/ 开头时自动补 /apps/<app_name>/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印上传计划，不联网、不要 token",
    )
    parser.add_argument(
        "--credentials-file",
        type=Path,
        help="仓库外的 0600 JSON（也可用环境变量 AMRH_BAIDU_CREDENTIALS_FILE）",
    )
    args = parser.parse_args()
    credentials = None
    try:
        credentials = load_credentials(credentials_file=args.credentials_file)
    except CredentialError as exc:
        if not args.dry_run:
            print(f"BAIDU UPLOAD: FAIL — {exc}", file=sys.stderr)
            print(
                "下一步：把 0600 JSON 放到仓库外，export AMRH_BAIDU_CREDENTIALS_FILE，"
                "或先加 --dry-run 只看计划。",
                file=sys.stderr,
            )
            return 2
    plan = plan_upload(args.local, args.remote, credentials)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("BAIDU UPLOAD: DRY-RUN (no network, no secrets printed)")
        if credentials is None:
            print(
                "下一步：凭证放仓库外（chmod 0600），"
                "export AMRH_BAIDU_CREDENTIALS_FILE 后再去掉 --dry-run。"
            )
        return 0
    assert credentials is not None
    try:
        result = upload(args.local, args.remote, credentials)
    except (OSError, RuntimeError, urllib.error.URLError) as exc:
        print(f"BAIDU UPLOAD: FAIL — {exc.__class__.__name__}", file=sys.stderr)
        return 1
    print(f"BAIDU UPLOAD: PASS remote={result['remote']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
