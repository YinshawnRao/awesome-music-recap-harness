#!/usr/bin/env python3
"""Bilibili video search with WBI signing.

Cookie jar is loaded only when a search actually runs. Importing this module
does not open cookies. Values are never printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import stat
import time
import urllib.parse
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
MIXIN_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


def default_cookie_path(repo_root: Path | None = None) -> Path:
    root = REPO_ROOT if repo_root is None else Path(repo_root)
    return root / "all_cookies.txt"


def mixin_key(img_url: str, sub_url: str) -> str:
    img_key = Path(urllib.parse.urlparse(img_url).path).stem
    sub_key = Path(urllib.parse.urlparse(sub_url).path).stem
    raw = img_key + sub_key
    return "".join(raw[index] for index in MIXIN_TAB)[:32]


def sign_params(params: dict[str, str], mixin: str) -> dict[str, str]:
    signed = dict(params)
    signed["wts"] = str(int(time.time()))
    query = urllib.parse.urlencode(sorted(signed.items()))
    signed["w_rid"] = hashlib.md5((query + mixin).encode("utf-8")).hexdigest()
    return signed


def _cookie_header(path: Path) -> str:
    if not path.is_file():
        return ""
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ValueError(f"cookie jar mode is {mode:04o}; chmod 600")
    pairs: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = line[len("#HttpOnly_"):] if line.startswith("#HttpOnly_") else line
        if not raw or raw.startswith("#"):
            continue
        fields = raw.split("\t")
        if len(fields) < 7:
            continue
        domain = fields[0].lstrip(".").lower()
        if domain == "bilibili.com" or domain.endswith(".bilibili.com"):
            pairs.append(f"{fields[5]}={fields[6]}")
    return "; ".join(pairs)


def search(keyword: str, limit: int = 5, *, cookies: Path | None = None) -> list[dict]:
    nav_req = urllib.request.Request(
        "https://api.bilibili.com/x/web-interface/nav",
        headers={"User-Agent": UA, "Referer": "https://www.bilibili.com/"},
    )
    with urllib.request.urlopen(nav_req, timeout=20) as response:
        nav = json.loads(response.read().decode("utf-8"))
    wbi = nav.get("data", {}).get("wbi_img", {})
    mixin = mixin_key(wbi["img_url"], wbi["sub_url"])
    params = sign_params(
        {"search_type": "video", "keyword": keyword},
        mixin,
    )
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type?" + urllib.parse.urlencode(params)
    headers = {"User-Agent": UA, "Referer": "https://www.bilibili.com/"}
    cookie_path = cookies or default_cookie_path()
    header = _cookie_header(cookie_path) if cookie_path.is_file() else ""
    if header:
        headers["Cookie"] = header
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    results = payload.get("data", {}).get("result") or []
    rows = []
    for item in results[:limit]:
        if not isinstance(item, dict):
            continue
        bvid = item.get("bvid")
        if not bvid:
            continue
        rows.append(
            {
                "bvid": bvid,
                "title": item.get("title", ""),
                "author": item.get("author", ""),
                "duration": item.get("duration", ""),
                "url": f"https://www.bilibili.com/video/{bvid}",
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keyword")
    parser.add_argument("limit", nargs="?", type=int, default=5)
    parser.add_argument("--cookies", type=Path)
    args = parser.parse_args()
    try:
        rows = search(args.keyword, args.limit, cookies=args.cookies)
    except Exception as exc:
        print(f"BILI SEARCH: FAIL — {exc.__class__.__name__}", flush=True)
        return 5
    if not rows:
        print("BILI SEARCH: EMPTY")
        return 1
    for row in rows:
        print(f"{row['bvid']} | {row['duration']} | {row['author']} | {row['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
