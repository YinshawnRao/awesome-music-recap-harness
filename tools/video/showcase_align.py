#!/usr/bin/env python3
"""Showcase window alignment helper.

Validates that a planned show window:
1. starts near vocal onset relative to narration end (about 2s early)
2. does not end inside an active sung word

Without Whisper analysis this tool can still check schema and emit a plan
skeleton. Hard FAIL cannot be overridden by approvals.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_window(window: dict, analysis: dict | None = None) -> str:
    required = ("narr_end_src", "show_start_src", "show_end_src")
    if any(key not in window for key in required):
        return "MISS"
    if window["show_end_src"] <= window["show_start_src"]:
        return "FAIL"
    if window["show_start_src"] + 0.5 < window["narr_end_src"] - 4:
        return "FAIL"
    if analysis is None:
        return "REVIEW"
    active = analysis.get("active_word_intervals") or []
    end = float(window["show_end_src"])
    for interval in active:
        start = float(interval[0])
        stop = float(interval[1])
        if start < end < stop - 0.12:
            return "FAIL"
    if analysis.get("evidence_level") == "multi_evidence":
        return "OK"
    return "REVIEW"


def gate(blocks: list[dict], vocals_path: Path | str | None, **_kwargs) -> dict:
    analysis = None
    if vocals_path and Path(vocals_path).is_file():
        analysis = load_json(Path(vocals_path))
    results = []
    for block in blocks:
        window = {
            "narr_end_src": block.get("narr_end") or block.get("narr_end_src"),
            "show_start_src": block.get("full_start") or block.get("show_start_src"),
            "show_end_src": block.get("end") or block.get("show_end_src"),
        }
        status = verify_window(window, analysis.get(block.get("id")) if analysis else None)
        results.append({"id": block.get("id"), "status": status, "window": window})
    fails = sum(1 for row in results if row["status"] == "FAIL")
    if fails:
        raise SystemExit(f"SHOWCASE ALIGN: FAIL fail={fails}")
    return {"results": results, "fail": fails}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    check = sub.add_parser("check")
    check.add_argument("--plan", type=Path, required=True)
    check.add_argument("--vocals", type=Path)
    plan = sub.add_parser("plan")
    plan.add_argument("--voice-dur", type=float, required=True)
    plan.add_argument("--near", type=float, required=True)
    args = parser.parse_args()
    if args.mode == "plan":
        lead = 0.3
        suggested = {
            "ch_off": round(args.near - (lead + args.voice_dur - 2.0), 3),
            "show": 25.0,
            "note": "Walk the cut backward from vocal onset; never slice a sung word.",
        }
        print(json.dumps(suggested, ensure_ascii=False, indent=2))
        return 0
    payload = load_json(args.plan)
    blocks = payload.get("blocks") or payload.get("items") or []
    try:
        report = gate(blocks, args.vocals)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("SHOWCASE ALIGN: PASS (REVIEW allowed without multi-evidence vocals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
