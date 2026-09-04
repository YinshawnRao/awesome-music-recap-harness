#!/usr/bin/env python3
"""TOP countdown planner / build template.

Reads a generic songs JSON (placeholder artists only in the flagship demo).
Default ``--plan-only`` writes timeline.json without calling ffmpeg. A later
full build can consume the same plan to mix master.wav and emit index.html.

N→1 is an internal playback order. Cover/intro copy must not print the
mechanism.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from outro_cta import FIXED_OUTRO_CTA
except ImportError:
    from tools.video.outro_cta import FIXED_OUTRO_CTA

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHOW = 25.0
LEAD = 0.3
DIG = 1.0
GAP_A = 1.2
DIGEST_O = 1.0
OUTRO_TAIL = 2.6


def _duration(wav: Path, fallback: float) -> float:
    if not wav.is_file():
        return fallback
    import contextlib
    import wave

    with contextlib.closing(wave.open(str(wav), "r")) as handle:
        return round(handle.getnframes() / handle.getframerate(), 3)


def load_songs(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not value.get("songs"):
        raise ValueError("songs file must contain a songs array")
    return value


def plan_timeline(config: dict, project: Path) -> dict:
    songs = list(config["songs"])
    ranks = [int(song["rank"]) for song in songs]
    expected = list(range(max(ranks), 0, -1))
    if ranks != expected:
        raise ValueError(f"songs must be listed N→1; got {ranks}")
    audio = project / config.get("audio_dir", "narration")
    d_intro = _duration(audio / "intro.wav", float(config.get("intro_seconds", 6.0)))
    d_outro = _duration(audio / "work-outro.wav", float(config.get("outro_seconds", 8.0)))
    d_cta = _duration(audio / "outro-cta.wav", float(config.get("cta_seconds", 10.0)))
    intro_voice_end = LEAD + d_intro
    cursor = intro_voice_end + GAP_A
    blocks = []
    for song in songs:
        key = song["id"]
        voice = _duration(
            audio / f"{key}.wav",
            float(song.get("transition_seconds", 5.0)),
        )
        show = float(song.get("show_seconds", config.get("show_default", DEFAULT_SHOW)))
        narr_start = cursor
        narr_end = narr_start + voice
        full_start = narr_end + 0.2 + DIG
        end = round(full_start + show, 3)
        blocks.append(
            {
                "id": key,
                "rank": song["rank"],
                "title": song["title"],
                "performer": song["performer"],
                "tag": song.get("tag", ""),
                "clip": song.get("clip", f"clips/vert_{key}.mp4"),
                "start": round(cursor, 3),
                "narr_start": round(narr_start, 3),
                "narr_end": round(narr_end, 3),
                "full_start": round(full_start, 3),
                "end": end,
                "show_seconds": show,
                "voice_seconds": voice,
            }
        )
        cursor = end
    f_start = cursor
    f_voice = f_start + LEAD
    f_voice_end = f_voice + d_outro
    f_cta = round(f_voice_end + DIGEST_O, 3)
    f_cta_end = round(f_cta + d_cta, 3)
    f_end = round(f_cta_end + OUTRO_TAIL, 3)
    return {
        "schema_version": 1,
        "project_kind": "top_ranking",
        "playback_order": "N→1",
        "canvas": {"width": 1080, "height": 1920, "fps": 30},
        "hyperframes": "0.6.69",
        "intro": {"start": 0.0, "voice_end": round(intro_voice_end, 3)},
        "blocks": blocks,
        "outro": {
            "start": round(f_start, 3),
            "work_outro_end": round(f_voice_end, 3),
            "cta_start": f_cta,
            "cta_end": f_cta_end,
            "end": f_end,
            "cta_text": FIXED_OUTRO_CTA,
        },
        "total_seconds": f_end,
        "mux": {
            "render": "renders/full.mp4",
            "master": "master.wav",
            "final": "renders/<slug>.mp4",
            "command": (
                "ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a "
                "-c:v copy -c:a aac -b:a 192k -shortest renders/<slug>.mp4"
            ),
        },
        "notes": [
            "Cover uses the first-played song (last place), not rank 1.",
            "Do not print N→1 on the cover or intro.",
            "HyperFrames render must pass --sdr and run via resource_budget.py.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--songs", type=Path, help="defaults to <project>/songs.json")
    parser.add_argument("--output", type=Path, help="defaults to <project>/timeline.json")
    parser.add_argument(
        "--plan-only",
        action="store_true",
        default=True,
        help="write timeline.json without mixing audio (v1 default)",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="reserved: 成片请用 python3 tools/cli.py smoke-e2e",
    )
    args = parser.parse_args()
    songs_path = args.songs or (args.project / "songs.json")
    output = args.output or (args.project / "timeline.json")
    try:
        config = load_songs(songs_path)
        timeline = plan_timeline(config, args.project)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"COUNTDOWN PLAN: FAIL — {exc}", file=sys.stderr)
        return 1
    output.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    print(
        f"COUNTDOWN PLAN: PASS items={len(timeline['blocks'])} "
        f"total={timeline['total_seconds']}s order=N→1"
    )
    if args.build:
        print(
            "COUNTDOWN BUILD: SKIP — 成片走 python3 tools/cli.py smoke-e2e "
            "（占位竖屏 + HyperFrames 0.6.69 --sdr → mux）。本命令只写 timeline.json。",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
