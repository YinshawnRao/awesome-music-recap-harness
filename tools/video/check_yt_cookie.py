#!/usr/bin/env python3
"""Static preflight for a YouTube Netscape cookie jar.

Does not network, repair, or print cookie values. Passing only means required
fields exist, file-internal expiry is in the future, and the file is not
group/other readable.
"""

from __future__ import annotations

import stat
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HTTPONLY_PREFIX = "#HttpOnly_"
REQUIRED = [
    "LOGIN_INFO",
    "SID",
    "HSID",
    "SSID",
    "SAPISID",
    "APISID",
    "__Secure-3PSID",
]
HELPFUL = [
    "__Secure-1PSID",
    "__Secure-1PAPISID",
    "__Secure-3PAPISID",
    "__Secure-1PSIDTS",
    "__Secure-3PSIDTS",
]
AUTH_HASH_NAMES = {"SAPISID", "__Secure-3PAPISID", "__Secure-1PAPISID"}
ALLOWED_DOMAIN_SUFFIXES = ("youtube.com", "google.com", "bilibili.com")


def default_cookie_path(repo_root: Path | None = None) -> Path:
    root = REPO_ROOT if repo_root is None else Path(repo_root)
    return root / "all_cookies.txt"


def _parse_netscape_line(line: str) -> tuple[str, str, str] | None:
    if not line.strip():
        return None
    if line.startswith(HTTPONLY_PREFIX):
        line = line[len(HTTPONLY_PREFIX) :]
    elif line.startswith("#"):
        return None
    fields = line.split("\t")
    if len(fields) < 7:
        return None
    return fields[0], fields[5], fields[4]


def load(path: Path | str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        row = _parse_netscape_line(line)
        if row is not None:
            rows.append(row)
    return rows


def _expiry_epoch(value: str) -> int | None:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return None


def _is_live(expiry: str, now: int) -> bool:
    epoch = _expiry_epoch(expiry)
    return epoch is not None and (epoch == 0 or epoch > now)


def _permission_check(path: Path) -> tuple[bool, str]:
    mode = stat.S_IMODE(path.stat().st_mode)
    return mode & 0o077 == 0, f"{mode:04o}"


def _allowed_domain(domain: str) -> bool:
    normalized = domain.removeprefix("#HttpOnly_").lstrip(".").lower()
    return any(normalized == suffix or normalized.endswith(f".{suffix}") for suffix in ALLOWED_DOMAIN_SUFFIXES)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("Usage: python3 tools/video/check_yt_cookie.py [cookie-file]")
        return 2
    path = Path(args[0]).expanduser() if args else default_cookie_path()
    if not path.is_file():
        print("Cookie file is missing (public downloads can continue without it)")
        return 2
    rows = load(path)
    now = int(time.time())
    domains = {domain for domain, _, _ in rows}
    by_name: dict[str, list[tuple[str, str]]] = {}
    for domain, name, expiry in rows:
        by_name.setdefault(name, []).append((domain, expiry))
    permission_ok, mode_text = _permission_check(path)
    print(f"file: {path.name}")
    print(f"cookie metadata rows: {len(rows)} (values discarded)")
    print(f"mode: {mode_text} " + ("ok" if permission_ok else "group/other readable"))
    unexpected_domains = {domain for domain in domains if not _allowed_domain(domain)}
    print(
        "extra-domain advisory: "
        + ("none" if not unexpected_domains else f"{len(unexpected_domains)} non-target domains")
    )
    ok = permission_ok

    def check(name: str, required: bool) -> bool:
        entries = by_name.get(name)
        if not entries:
            print(f"  {'missing' if required else 'optional-missing'} {name}")
            return not required
        live_expiries = [expiry for _, expiry in entries if _is_live(expiry, now)]
        if not live_expiries:
            print(f"  expired {name}")
            return not required
        print(f"  live {name}")
        return True

    print("required:")
    for name in REQUIRED:
        if not check(name, True):
            ok = False
    print("helpful:")
    for name in HELPFUL:
        check(name, False)
    can_hash = any(
        name in by_name and any(_is_live(expiry, now) for _, expiry in by_name[name])
        for name in AUTH_HASH_NAMES
    )
    if not can_hash:
        print("no live SAPISID / __Secure-*APISID")
        ok = False
    print("static preflight: " + ("PASS" if ok else "FAIL"))
    print("This check cannot prove the server still accepts the session.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
