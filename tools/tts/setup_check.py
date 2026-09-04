#!/usr/bin/env python3
"""Mac Qwen/MLX 配音体检：Metal、环境变量、模型树、参考 WAV。

缺任何一项就失败退出，并打印可执行的中文下一步。绝不改用 Kokoro。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
_REPO_ROOT = str(Path(_SCRIPT_DIR).parents[1])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from tools.tts.qwen_env import DEMO_VOICE_ID, format_report, inspect_setup
except ImportError:
    if _SCRIPT_DIR not in sys.path:
        sys.path.insert(0, _SCRIPT_DIR)
    from qwen_env import DEMO_VOICE_ID, format_report, inspect_setup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--voice",
        default=DEMO_VOICE_ID,
        help=f"要检查的声槽（默认教学项目 {DEMO_VOICE_ID}）",
    )
    parser.add_argument(
        "--skip-mlx-import",
        action="store_true",
        help="只看路径，不在 Qwen 解释器里 import mlx-audio（排错用）",
    )
    args = parser.parse_args(argv)
    report = inspect_setup(args.voice, check_mlx_import=not args.skip_mlx_import)
    text = format_report(report)
    stream = sys.stdout if report.ok else sys.stderr
    print(text, file=stream)
    return 0 if report.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
