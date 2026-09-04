#!/usr/bin/env python3
"""Thin dispatcher for the public AMRH command surface."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

COMMANDS = {
    "tts-doctor": TOOLS / "tts" / "doctor.py",
    "tts-resolve": TOOLS / "tts" / "resolve_voice.py",
    "tts-narrate": TOOLS / "tts" / "narrate.py",
    "tts-verify": TOOLS / "tts" / "verify_voice_usage.py",
    "project-verify": TOOLS / "video" / "verify_project.py",
    "publishing-verify": TOOLS / "video" / "verify_publishing.py",
    "final-qa": TOOLS / "video" / "prepare_final_qa.py",
    "countdown-plan": TOOLS / "video" / "countdown_build.py",
    "yt-dlp": TOOLS / "video" / "yt_dlp_readonly.py",
    "cookie-check": TOOLS / "video" / "check_yt_cookie.py",
    "bili-search": TOOLS / "video" / "bili_search.py",
    "baidu-upload": TOOLS / "delivery" / "baidu" / "upload.py",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="amrh",
        description="Awesome Music Recap Harness — public CLI for gates and helpers.",
    )
    parser.add_argument("command", choices=sorted(COMMANDS), help="tool to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="arguments for the tool")
    ns = parser.parse_args(argv)
    script = COMMANDS[ns.command]
    forwarded = list(ns.args)
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    sys.argv = [str(script), *forwarded]
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
