#!/usr/bin/env python3
"""Bilibili download helper (412 fallback).

When yt-dlp's Bilibili extractor hits HTTP 412, a browser-style page fetch can
still expose ``window.__playinfo__`` DASH URLs. This helper documents that
path and refuses to put cookie values on argv.

v1 implementation: print the intended curl + ffmpeg steps. Live download is
opt-in via --execute once the user has a readable 0600 cookie jar.
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def plan(bvid: str, output: Path, max_h: int = 1080) -> list[str]:
    url = f"https://www.bilibili.com/video/{bvid}"
    cookies = REPO_ROOT / "all_cookies.txt"
    return [
        f"# Fetch playinfo for {bvid} (cookie jar stays on disk, never in argv values)",
        "curl --compressed -A 'Mozilla/5.0' -e 'https://www.bilibili.com/' "
        + (f"--cookie {shlex.quote(str(cookies))} " if cookies.is_file() else "")
        + shlex.quote(url),
        f"# Parse window.__playinfo__, pick video height<={max_h} (prefer AVC) + best audio",
        f"# curl the two m4s URLs, then: ffmpeg -i video.m4s -i audio.m4s -c copy {shlex.quote(str(output))}",
        "# Prefer the cookie-safe yt-dlp wrapper first:",
        f"python3 tools/video/yt_dlp_readonly.py -- {shlex.quote(url)} "
        f"-f 'bv*[height<={max_h}]+ba/b[height<={max_h}]' -o {shlex.quote(str(output))}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bvid")
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-h", type=int, default=1080)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="reserved: live DASH fetch is a follow-up; v1 prints the plan",
    )
    args = parser.parse_args()
    for line in plan(args.bvid, args.output, args.max_h):
        print(line)
    if args.execute:
        print("BILI DL: SKIP execute — live DASH mux is documented, not shipped in v1", file=sys.stderr)
        return 2
    print("BILI DL: PLAN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
