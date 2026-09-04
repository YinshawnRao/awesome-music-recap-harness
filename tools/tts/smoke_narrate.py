#!/usr/bin/env python3
"""P2 配音烟雾：先体检，再生成一句短旁白；可选整批教学项目。

缺权重 / Metal / 参考 WAV 就失败，并打印中文下一步。绝不改用 Kokoro。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from tools.tts.qwen_env import (
        DEMO_VOICE_ID,
        KOKORO_BAN,
        SetupError,
        format_report,
        inspect_setup,
        require_generation_ready,
    )
except ImportError:
    if _SCRIPT_DIR not in sys.path:
        sys.path.insert(0, _SCRIPT_DIR)
    from qwen_env import (
        DEMO_VOICE_ID,
        KOKORO_BAN,
        SetupError,
        format_report,
        inspect_setup,
        require_generation_ready,
    )


DEFAULT_PROJECT = REPO_ROOT / "examples" / "top-ranking-demo"
SMOKE_TEXT = "配音烟雾。这是一句很短的测试。"
SMOKE_REL = Path("audio") / "smoke.wav"


def _run_narrate(args: list[str]) -> int:
    command = [sys.executable, str(Path(_SCRIPT_DIR) / "narrate.py"), *args]
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


def run_smoke(
    project: Path,
    *,
    voice_id: str = DEMO_VOICE_ID,
    full: bool = False,
    check_only: bool = False,
) -> int:
    selection = project / "voice-selection.json"
    request = project / "narration-request.json"
    smoke_out = project / SMOKE_REL

    print("SMOKE NARRATE — 先体检，再生成一句短旁白。", flush=True)
    report = inspect_setup(voice_id)
    print(format_report(report), flush=True)
    if not report.ok:
        print(f"SMOKE NARRATE: FAIL — 安装检查没过。{KOKORO_BAN}")
        return 2
    if check_only:
        print("SMOKE NARRATE: PASS check-only（尚未生成 WAV）")
        return 0

    try:
        require_generation_ready(voice_id)
    except SetupError as error:
        print(str(error))
        print(f"SMOKE NARRATE: FAIL — {KOKORO_BAN}")
        return 2

    if not selection.is_file():
        print(f"SMOKE NARRATE: FAIL — 缺少 {selection}")
        return 2

    print(flush=True)
    print(f"一句烟雾 → {smoke_out}", flush=True)
    code = _run_narrate(
        [SMOKE_TEXT, "--selection-file", str(selection), "-o", str(smoke_out)]
    )
    if code != 0 or not smoke_out.is_file():
        print()
        print("SMOKE NARRATE: FAIL — 短句没有写出 WAV。")
        print("下一步：python3 tools/tts/setup_check.py")
        print(KOKORO_BAN)
        return 1

    print()
    print("SMOKE NARRATE: PASS")
    print(f"  {smoke_out}")

    if not full:
        print()
        print("整批教学旁白（可选）：")
        print("  python3 tools/cli.py smoke-narrate -- --full")
        print("结构门禁（不需要 WAV）：")
        print(
            "  python3 tools/tts/verify_voice_usage.py "
            f"--selection {selection} --project-root {project}"
        )
        print("真 WAV 门禁：")
        print(
            "  python3 tools/tts/verify_voice_usage.py "
            f"--selection {selection} --project-root {project} --require-wav"
        )
        return 0

    if not request.is_file():
        print(f"SMOKE NARRATE: FAIL — 缺少 {request}")
        return 2
    print(flush=True)
    print(f"整批 → {request}", flush=True)
    batch_code = _run_narrate(
        ["--batch", str(request), "--selection-file", str(selection)]
    )
    if batch_code != 0:
        print("SMOKE NARRATE: FAIL — 整批配音失败。短句已经成功，先看 setup_check。")
        return 1
    print()
    print("SMOKE NARRATE: PASS full")
    print("真 WAV 门禁：")
    print(
        "  python3 tools/tts/verify_voice_usage.py "
        f"--selection {selection} --project-root {project} --require-wav"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=DEFAULT_PROJECT,
        help="教学项目目录（默认 examples/top-ranking-demo）",
    )
    parser.add_argument("--voice", default=DEMO_VOICE_ID)
    parser.add_argument(
        "--full",
        action="store_true",
        help="短句成功后再跑 narration-request.json 整批",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="只跑安装检查，不调用模型",
    )
    args = parser.parse_args(argv)
    return run_smoke(
        args.project.resolve(),
        voice_id=args.voice,
        full=args.full,
        check_only=args.check_only,
    )


if __name__ == "__main__":
    raise SystemExit(main())
