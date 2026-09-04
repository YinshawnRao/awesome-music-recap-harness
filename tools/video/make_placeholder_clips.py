#!/usr/bin/env python3
"""Generate short legal placeholder vertical clips for the TOP teaching project.

No network. No copyrighted MVs. ffmpeg colorbars / solid color + optional beep.
Writes gitignored binaries under footage/ and clips/ so P1 can run offline.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = REPO_ROOT / "examples" / "top-ranking-demo"
DEFAULT_SECONDS = 4
WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Distinct solids so the five ranks are visually separable. rank-05 uses bars.
RANK_COLORS = {
    "rank-05": "smptebars",
    "rank-04": "0xEE6C4D",
    "rank-03": "0x3D5A80",
    "rank-02": "0x98C1D9",
    "rank-01": "0x293241",
}

DEFAULT_RANKS: list[dict[str, object]] = [
    {"id": "rank-05", "rank": 5, "title": "纸灯笼", "clip": "clips/vert_rank-05.mp4"},
    {"id": "rank-04", "rank": 4, "title": "夜渡", "clip": "clips/vert_rank-04.mp4"},
    {"id": "rank-03", "rank": 3, "title": "玻璃港", "clip": "clips/vert_rank-03.mp4"},
    {"id": "rank-02", "rank": 2, "title": "北窗", "clip": "clips/vert_rank-02.mp4"},
    {"id": "rank-01", "rank": 1, "title": "末班月台", "clip": "clips/vert_rank-01.mp4"},
]


class PlaceholderClipError(RuntimeError):
    """User-actionable generator failure."""


def load_ranks(project: Path) -> list[dict[str, object]]:
    songs_path = project / "songs.json"
    if not songs_path.is_file():
        return list(DEFAULT_RANKS)
    data = json.loads(songs_path.read_text(encoding="utf-8"))
    songs = data.get("songs") if isinstance(data, dict) else None
    if not isinstance(songs, list) or not songs:
        return list(DEFAULT_RANKS)
    ranks: list[dict[str, object]] = []
    for song in songs:
        if not isinstance(song, dict) or not song.get("id"):
            continue
        ranks.append(
            {
                "id": str(song["id"]),
                "rank": song.get("rank"),
                "title": song.get("title") or song["id"],
                "clip": song.get("clip") or f"clips/vert_{song['id']}.mp4",
            }
        )
    return ranks or list(DEFAULT_RANKS)


def _video_source(item_id: str) -> str:
    color = RANK_COLORS.get(item_id, "0x555555")
    if color == "smptebars":
        return f"smptebars=size={WIDTH}x{HEIGHT}:rate={FPS}"
    return f"color=c={color}:s={WIDTH}x{HEIGHT}:r={FPS}"


def _ffmpeg_command(
    dest: Path,
    item_id: str,
    *,
    seconds: float,
    beep: bool,
    ffmpeg: str,
) -> list[str]:
    video = _video_source(item_id)
    if beep:
        audio = "sine=frequency=880:sample_rate=48000:duration=0.25"
    else:
        audio = "anullsrc=channel_layout=stereo:sample_rate=48000"
    return [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        video,
        "-f",
        "lavfi",
        "-i",
        audio,
        "-t",
        f"{seconds:g}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-r",
        str(FPS),
        "-c:a",
        "aac",
        "-ac",
        "2",
        "-ar",
        "48000",
        "-b:a",
        "128k",
        "-shortest",
        str(dest),
    ]


def _run_ffmpeg(command: Sequence[str]) -> None:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as error:
        raise PlaceholderClipError(f"无法启动 ffmpeg：{error}") from error
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip().splitlines()
        hint = detail[-1] if detail else f"exit {completed.returncode}"
        raise PlaceholderClipError(f"ffmpeg 失败：{hint}")


def generate_placeholder_clips(
    project: Path,
    *,
    seconds: float = DEFAULT_SECONDS,
    beep: bool = True,
    footage_dir: Path | None = None,
    write_clips: bool = True,
    ffmpeg: str | None = None,
) -> list[Path]:
    if seconds <= 0:
        raise PlaceholderClipError("时长必须大于 0")
    binary = ffmpeg or shutil.which("ffmpeg")
    if not binary:
        raise PlaceholderClipError("找不到 ffmpeg。Mac：brew install ffmpeg。")

    ranks = load_ranks(project)
    footage = footage_dir if footage_dir is not None else project / "footage"
    footage.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for item in ranks:
        item_id = str(item["id"])
        footage_path = footage / f"{item_id}.mp4"
        _run_ffmpeg(
            _ffmpeg_command(
                footage_path,
                item_id,
                seconds=seconds,
                beep=beep,
                ffmpeg=binary,
            )
        )
        written.append(footage_path)
        if write_clips:
            clip_rel = str(item.get("clip") or f"clips/vert_{item_id}.mp4")
            clip_path = project / clip_rel
            clip_path.parent.mkdir(parents=True, exist_ok=True)
            if clip_path.resolve() != footage_path.resolve():
                shutil.copyfile(footage_path, clip_path)
                written.append(clip_path)

    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="为 TOP 教学项目生成合法占位竖屏（不联网、不是版权 MV）。",
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=DEFAULT_PROJECT,
        help="项目目录（默认：examples/top-ranking-demo）",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=DEFAULT_SECONDS,
        help=f"每条时长秒数（默认 {DEFAULT_SECONDS}）",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="不要短鸣，只铺静音音轨（vfill 仍需要音轨）",
    )
    parser.add_argument(
        "--footage-only",
        action="store_true",
        help="只写 footage/，不拷到 clips/",
    )
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        written = generate_placeholder_clips(
            project,
            seconds=args.seconds,
            beep=not args.silent,
            write_clips=not args.footage_only,
        )
    except PlaceholderClipError as error:
        print(f"PLACEHOLDER CLIPS: FAIL — {error}")
        return 2
    print("PLACEHOLDER CLIPS: PASS")
    print("这些是本机生成的色条 / 色块，不是版权 MV。P1 教学用它们代替 example.com。")
    print("换成真实官方 URL 是后面的事，见 SOURCES.md。")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
