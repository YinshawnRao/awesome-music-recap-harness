#!/usr/bin/env python3
"""Build master.wav for the TOP teaching project.

Two honest paths (both produce a muxable stereo WAV):

1. 旁白 WAV 齐了：按 smoke-timeline.json 把各段铺到时间线（缺的段落留静音）。
2. 只有 sidecar、没有 WAV：铺整段静音床；``--tone`` 改成很轻的 440 Hz 正弦，
   方便确认成片有声轨。这不是配音，也不能拿去过「>1.5s 静音」硬门禁。

不把 WAV 提交进 git。需要 ffmpeg 才能叠真实旁白；静音 / 短鸣只靠标准库。
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = REPO_ROOT / "examples" / "top-ranking-demo"
DEFAULT_TIMELINE = "smoke-timeline.json"
SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2
TONE_HZ = 440
TONE_AMPLITUDE = 0.08


class MixMasterError(RuntimeError):
    """User-actionable mix failure."""


def load_smoke_timeline(project: Path, name: str = DEFAULT_TIMELINE) -> dict[str, Any]:
    path = project / name
    if not path.is_file():
        raise MixMasterError(f"找不到 {name}。教学项目应已提交这份烟雾时间线。")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data.get("sections"):
        raise MixMasterError(f"{name} 必须包含 sections 数组")
    return data


def _frame_count(seconds: float) -> int:
    return max(1, int(round(float(seconds) * SAMPLE_RATE)))


def _silence_frames(frames: int) -> bytes:
    return b"\x00" * (frames * CHANNELS * SAMPLE_WIDTH)


def _tone_frames(frames: int) -> bytes:
    out = bytearray()
    two_pi = 2.0 * math.pi
    peak = int(TONE_AMPLITUDE * 32767)
    for index in range(frames):
        sample = int(peak * math.sin(two_pi * TONE_HZ * (index / SAMPLE_RATE)))
        packed = struct.pack("<hh", sample, sample)
        out.extend(packed)
    return bytes(out)


def write_bed(dest: Path, seconds: float, *, tone: bool) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    frames = _frame_count(seconds)
    payload = _tone_frames(frames) if tone else _silence_frames(frames)
    with wave.open(str(dest), "w") as handle:
        handle.setnchannels(CHANNELS)
        handle.setsampwidth(SAMPLE_WIDTH)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(payload)
    return dest


def existing_narration_wavs(project: Path, timeline: dict[str, Any]) -> list[Path]:
    found: list[Path] = []
    for section in timeline.get("sections") or []:
        rel = section.get("wav")
        if not rel:
            continue
        path = project / str(rel)
        if path.is_file():
            found.append(path)
    return found


def _run_ffmpeg(command: list[str]) -> None:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as error:
        raise MixMasterError(f"无法启动 ffmpeg：{error}") from error
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip().splitlines()
        hint = detail[-1] if detail else f"exit {completed.returncode}"
        raise MixMasterError(f"ffmpeg 混音失败：{hint}")


def mix_from_wavs(
    project: Path,
    timeline: dict[str, Any],
    dest: Path,
    *,
    ffmpeg: str,
) -> Path:
    duration = float(timeline["duration"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    inputs: list[str] = []
    filters: list[str] = []
    mixed: list[str] = []
    index = 0
    for section in timeline["sections"]:
        rel = section.get("wav")
        if not rel:
            continue
        path = project / str(rel)
        if not path.is_file():
            continue
        start = float(section.get("start") or 0)
        inputs.extend(["-i", str(path)])
        label = f"a{index}"
        filters.append(
            f"[{index}:a]aformat=sample_fmts=s16:sample_rates={SAMPLE_RATE}"
            f":channel_layouts=stereo,adelay={int(round(start * 1000))}|"
            f"{int(round(start * 1000))}[{label}]"
        )
        mixed.append(f"[{label}]")
        index += 1
    if not mixed:
        raise MixMasterError("没有可叠的旁白 WAV")
    filters.append(
        f"{''.join(mixed)}amix=inputs={len(mixed)}:dropout_transition=0:normalize=0[mixed];"
        f"[mixed]apad=whole_dur={duration:g},atrim=0:{duration:g},aformat="
        f"sample_fmts=s16:sample_rates={SAMPLE_RATE}:channel_layouts=stereo[aout]"
    )
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        *inputs,
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[aout]",
        "-t",
        f"{duration:g}",
        "-c:a",
        "pcm_s16le",
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        str(CHANNELS),
        str(dest),
    ]
    _run_ffmpeg(command)
    return dest


def mix_master(
    project: Path,
    *,
    dest: Path | None = None,
    timeline_name: str = DEFAULT_TIMELINE,
    tone: bool = False,
    ffmpeg: str | None = None,
) -> tuple[Path, str]:
    """Return (path, mode) where mode is wav | silent | tone."""

    timeline = load_smoke_timeline(project, timeline_name)
    duration = float(timeline["duration"])
    target = dest or (project / "master.wav")
    wavs = existing_narration_wavs(project, timeline)
    if wavs:
        binary = ffmpeg or shutil.which("ffmpeg")
        if not binary:
            raise MixMasterError("有旁白 WAV，但找不到 ffmpeg。Mac：brew install ffmpeg。")
        mix_from_wavs(project, timeline, target, ffmpeg=binary)
        return target, "wav"
    write_bed(target, duration, tone=tone)
    return target, "tone" if tone else "silent"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=DEFAULT_PROJECT,
        help="项目目录（默认：examples/top-ranking-demo）",
    )
    parser.add_argument("--output", type=Path, help="默认写 <project>/master.wav")
    parser.add_argument(
        "--timeline",
        default=DEFAULT_TIMELINE,
        help="相对项目目录的烟雾时间线（默认 smoke-timeline.json）",
    )
    parser.add_argument(
        "--tone",
        action="store_true",
        help="没有旁白 WAV 时铺轻正弦，而不是静音床",
    )
    args = parser.parse_args(argv)
    project = args.project.resolve()
    try:
        path, mode = mix_master(
            project,
            dest=args.output.resolve() if args.output else None,
            timeline_name=args.timeline,
            tone=args.tone,
        )
    except (OSError, json.JSONDecodeError, ValueError, MixMasterError) as error:
        print(f"MIX MASTER: FAIL — {error}")
        return 2
    labels = {
        "wav": "已按旁白 WAV 预混",
        "silent": "没有旁白 WAV，铺了静音床（视觉烟雾用，不是可发布成片）",
        "tone": "没有旁白 WAV，铺了轻正弦床（确认有声轨，不是配音）",
    }
    print(f"MIX MASTER: PASS mode={mode}")
    print(labels[mode])
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
