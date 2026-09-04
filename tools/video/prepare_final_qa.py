#!/usr/bin/env python3
"""FINAL VIDEO QA preparer (structure stub for v1).

A full ASR / frame-hash / loudness gate is a follow-up. This command checks
that a structured project declared the files a later machine gate will need,
and writes a pending qa/final-video-qa.json skeleton.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def prepare(project: Path, final: Path | None, render: Path | None) -> dict:
    manifest = project / "project-manifest.json"
    timeline = project / "timeline.json"
    missing = []
    if not manifest.is_file():
        missing.append("project-manifest.json")
    if not timeline.is_file():
        missing.append("timeline.json")
    payload = {
        "schema_version": 1,
        "status": "pending_machine_qa",
        "project_kind": None,
        "assets": {
            "final": {"path": str(final) if final else "renders/<slug>.mp4"},
            "render": {"path": str(render) if render else "renders/full.mp4"},
            "master": {"path": "master.wav"},
        },
        "checks": {
            "expected_video_codec": "h264",
            "silence_hard_fail_sec": 1.5,
            "loudness_lufs": [-20, -10],
            "true_peak_dbtp_max": -0.1,
        },
        "reviews": {
            "visual_frames": "pending_human_review",
            "leakage": "pending_human_review",
            "release_safety": "pending_human_review",
        },
        "notes": [
            "v1 writes a skeleton only. Do not claim machine understanding of frames.",
            "Never forge reviewer_kind=human.",
            "Full Whisper/ffmpeg diagnostics are a documented follow-up.",
        ],
        "missing_inputs": missing,
    }
    if manifest.is_file():
        authoring = json.loads(manifest.read_text(encoding="utf-8"))
        payload["project_kind"] = authoring.get("project_kind")
        payload["authoring_manifest"] = {"path": "project-manifest.json"}
    qa_dir = project / "qa"
    qa_dir.mkdir(exist_ok=True)
    target = qa_dir / "final-video-qa.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["qa_path"] = str(target)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--final", type=Path)
    parser.add_argument("--render", type=Path)
    parser.add_argument(
        "--require-human-review",
        action="store_true",
        help="publish mode: v1 still returns REVIEW_REQUIRED because no human input is merged",
    )
    args = parser.parse_args()
    payload = prepare(args.project, args.final, args.render)
    if args.require_human_review:
        print("FINAL VIDEO QA: REVIEW_REQUIRED (no human-review-input merged)")
        return 2
    print(payload["qa_path"])
    print("FINAL VIDEO QA: PASS skeleton pending_machine_qa")
    if payload["missing_inputs"]:
        print("advisories=" + ",".join(payload["missing_inputs"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
