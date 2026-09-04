#!/usr/bin/env python3
"""Static preflight for the dual-platform Netscape cookie jar.

Does not network, repair, or print cookie values. Passing only means required
YouTube/Google and Bilibili fields exist, file-internal expiry is in the
future, permissions are user-only, and values are not demo placeholders.
The committed example jar is format-only; it must fail this check until the
operator replaces placeholder tokens with a real export.
"""

from __future__ import annotations

import stat
import sys
import time
from dataclasses import dataclass
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
REQUIRED_BILIBILI = [
    "SESSDATA",
    "bili_jct",
    "DedeUserID",
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
PLACEHOLDER_MARKERS = (
    "PLACEHOLDER",
    "NOT_A_SESSION",
    "EXAMPLE",
    "FAKESECRET",
)
MISSING_JAR_HINT = (
    "Cookie file is missing. The full dual-platform yt-dlp pipeline requires "
    "repo-root all_cookies.txt (mode 0600). Copy "
    "examples/cookies/all_cookies.example.txt, chmod 0600, then replace "
    "placeholder values with a real Netscape export. Structure-only gates "
    "can still run without a jar."
)


def default_cookie_path(repo_root: Path | None = None) -> Path:
    root = REPO_ROOT if repo_root is None else Path(repo_root)
    return root / "all_cookies.txt"


def _parse_netscape_line(line: str) -> tuple[str, str, str, str] | None:
    if not line.strip():
        return None
    if line.startswith(HTTPONLY_PREFIX):
        line = line[len(HTTPONLY_PREFIX) :]
    elif line.startswith("#"):
        return None
    fields = line.split("\t")
    if len(fields) < 7:
        return None
    return fields[0], fields[5], fields[4], fields[6]


def _looks_like_placeholder(value: str) -> bool:
    upper = value.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


@dataclass(frozen=True)
class CookieJarInspection:
    """Metadata-only view of a Netscape jar. Values are never retained."""

    rows: list[tuple[str, str, str]]
    placeholder_values: bool


def inspect_jar(path: Path | str) -> CookieJarInspection:
    rows: list[tuple[str, str, str]] = []
    placeholder_values = False
    for line in Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        parsed = _parse_netscape_line(line)
        if parsed is None:
            continue
        domain, name, expiry, value = parsed
        if _looks_like_placeholder(value):
            placeholder_values = True
        rows.append((domain, name, expiry))
    return CookieJarInspection(rows=rows, placeholder_values=placeholder_values)


def load(path: Path | str) -> list[tuple[str, str, str]]:
    return inspect_jar(path).rows


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
        print(MISSING_JAR_HINT)
        return 2
    inspection = inspect_jar(path)
    rows = inspection.rows
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
    if inspection.placeholder_values:
        print(
            "placeholder-value advisory: demo tokens present; replace them "
            "with a real Netscape export before download (values not printed)"
        )
    else:
        print("placeholder-value advisory: none")
    ok = permission_ok and not inspection.placeholder_values

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

    print("required YouTube/Google:")
    for name in REQUIRED:
        if not check(name, True):
            ok = False
    print("required Bilibili:")
    for name in REQUIRED_BILIBILI:
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
