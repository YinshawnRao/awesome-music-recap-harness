#!/usr/bin/env python3
"""Batch-narrate helper that only talks to the central TTS entry."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NARRATE = REPO_ROOT / "tools" / "tts" / "narrate.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--request", type=Path, help="defaults to <project>/narration-request.json")
    parser.add_argument("--selection", type=Path, help="defaults to <project>/voice-selection.json")
    parser.add_argument(
        "--real",
        action="store_true",
        help="真生成 WAV（缺权重就失败，不改用 Kokoro）。默认仍是 --dry-run sidecar。",
    )
    args = parser.parse_args()
    request = args.request or (args.project / "narration-request.json")
    selection = args.selection or (args.project / "voice-selection.json")
    if not request.is_file() or not selection.is_file():
        print("NARRATE SEGMENTS: FAIL — request or selection missing", file=sys.stderr)
        return 2
    command = [
        sys.executable,
        str(NARRATE),
        "--batch",
        str(request),
        "--selection-file",
        str(selection),
    ]
    if not args.real:
        command.append("--dry-run")
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
