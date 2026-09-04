#!/usr/bin/env python3
"""Multi-evidence lead-vocal candidate helper.

v1 ships the schema and a dry-run writer. Real Whisper/librosa analysis is
optional (``pip install '.[asr]'``) and is a documented follow-up. Energy-only
results must stay at evidence_level=energy_candidate and never auto-OK.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def placeholder_analysis(clip: Path) -> dict:
    return {
        "schema_version": 1,
        "clip": clip.name,
        "evidence_level": "placeholder",
        "lead_segments": [],
        "vocal_segments": [],
        "safe_cut_intervals": [],
        "active_word_intervals": [],
        "notes": [
            "No Whisper model was loaded.",
            "Replace this file after running --mode multi on a real clip.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clips", nargs="+", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("energy", "multi"), default="multi")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--source-kind", choices=("studio", "live"), default="studio")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="write a schema-valid placeholder (v1 default)",
    )
    args = parser.parse_args()
    payload = {
        "schema_version": 1,
        "mode": args.mode,
        "language": args.language,
        "source_kind": args.source_kind,
        "clips": {clip.name: placeholder_analysis(clip) for clip in args.clips},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    print("VOCAL SEGMENTS: PASS placeholder (install extras [asr] for multi-evidence)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
