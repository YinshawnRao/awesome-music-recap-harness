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
    "tts-setup": TOOLS / "tts" / "setup_check.py",
    "install-reference": TOOLS / "tts" / "install_reference.py",
    "smoke-narrate": TOOLS / "tts" / "smoke_narrate.py",
    "project-verify": TOOLS / "video" / "verify_project.py",
    "publishing-verify": TOOLS / "video" / "verify_publishing.py",
    "final-qa": TOOLS / "video" / "prepare_final_qa.py",
    "countdown-plan": TOOLS / "video" / "countdown_build.py",
    "yt-dlp": TOOLS / "video" / "yt_dlp_readonly.py",
    "cookie-check": TOOLS / "video" / "check_yt_cookie.py",
    "install-cookies": TOOLS / "video" / "install_cookies.py",
    "smoke-download": TOOLS / "video" / "smoke_download.py",
    "placeholder-clips": TOOLS / "video" / "make_placeholder_clips.py",
    "mix-master": TOOLS / "video" / "mix_master.py",
    "smoke-e2e": TOOLS / "video" / "smoke_e2e.py",
    "bili-search": TOOLS / "video" / "bili_search.py",
    "baidu-upload": TOOLS / "delivery" / "baidu" / "upload.py",
}

EPILOG = """
常用（从仓库根目录）：
  python3 tools/cli.py smoke-e2e -- --structure-only
  python3 tools/cli.py publishing-verify -- --project examples/top-ranking-demo
  python3 tools/cli.py baidu-upload --help
  python3 tools/cli.py baidu-upload -- --dry-run --local README.md --remote /apps/amrh/readme.md

子命令的 --help 会转发给对应脚本。CI 只跑结构门禁；Chrome / Qwen / 真 Cookie 仍在 Mac 上。
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/cli.py",
        description="音乐盘点工作台公开命令：门禁、烟雾、可选百度上传。",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("command", choices=sorted(COMMANDS), help="要跑的工具")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="转发给该工具的参数")
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
