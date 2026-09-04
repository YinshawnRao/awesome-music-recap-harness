from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.video.make_placeholder_clips import (
    DEFAULT_RANKS,
    generate_placeholder_clips,
    load_ranks,
    main as clips_main,
)


def _probe_stream(path: Path) -> dict[str, str]:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    streams = json.loads(completed.stdout).get("streams") or []
    assert streams
    return streams[0]


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
def test_generates_five_vertical_clips(tmp_path: Path) -> None:
    songs = {
        "songs": [
            {
                "id": item["id"],
                "rank": item["rank"],
                "title": item["title"],
                "clip": item["clip"],
            }
            for item in DEFAULT_RANKS
        ]
    }
    (tmp_path / "songs.json").write_text(
        json.dumps(songs, ensure_ascii=False), encoding="utf-8"
    )
    written = generate_placeholder_clips(tmp_path, seconds=0.5, beep=True)
    footage = [path for path in written if path.parent.name == "footage"]
    clips = [path for path in written if path.parent.name == "clips"]
    assert len(footage) == 5
    assert len(clips) == 5
    for path in footage:
        info = _probe_stream(path)
        assert int(info["width"]) == 1080
        assert int(info["height"]) == 1920
        assert path.stat().st_size > 0


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg required")
def test_cli_footage_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert clips_main(["--project", str(tmp_path), "--seconds", "0.4", "--footage-only"]) == 0
    captured = capsys.readouterr().out
    assert "PLACEHOLDER CLIPS: PASS" in captured
    assert (tmp_path / "footage" / "rank-05.mp4").is_file()
    assert not (tmp_path / "clips").exists()


def test_load_ranks_falls_back_without_songs(tmp_path: Path) -> None:
    ranks = load_ranks(tmp_path)
    assert [item["id"] for item in ranks] == [item["id"] for item in DEFAULT_RANKS]
