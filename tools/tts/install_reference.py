#!/usr/bin/env python3
"""把用户自录的 reference.wav 装进教学声槽（默认 CV007）。

写入 gitignore 路径 tools/tts/voices/local/<CVxxx>/reference.wav。
绝不提交真实 WAV。缺文件或格式不对就失败，并打印中文下一步。
"""

from __future__ import annotations

import argparse
import shutil
import struct
import sys
import wave
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
_REPO_ROOT = str(Path(_SCRIPT_DIR).parents[1])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from tools.tts.qwen_env import DEMO_VOICE_ID, SetupError
    from tools.tts.voice_registry import VoiceRegistry
except ImportError:
    if _SCRIPT_DIR not in sys.path:
        sys.path.insert(0, _SCRIPT_DIR)
    from qwen_env import DEMO_VOICE_ID, SetupError
    from voice_registry import VoiceRegistry


MIN_SECONDS = 3.0
WARN_LOW = 8.0
WARN_HIGH = 15.0
MAX_SECONDS = 45.0
TARGET_RATE = 24000


def _wav_info(path: Path) -> tuple[int, int, float]:
    try:
        with wave.open(str(path), "rb") as handle:
            channels = handle.getnchannels()
            rate = handle.getframerate()
            frames = handle.getnframes()
            width = handle.getsampwidth()
    except wave.Error as error:
        raise SetupError(f"不是可读的 WAV：{path.name}（{error}）") from error
    if channels < 1 or rate < 1 or frames < 1 or width < 1:
        raise SetupError(f"WAV 头不完整：{path.name}")
    duration = frames / float(rate)
    return channels, rate, duration


def _pcm_frames(path: Path) -> tuple[bytes, int, int, int]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        rate = handle.getframerate()
        width = handle.getsampwidth()
        frames = handle.readframes(handle.getnframes())
    return frames, channels, rate, width


def _to_mono_pcm(frames: bytes, channels: int, width: int) -> bytes:
    if channels == 1:
        return frames
    if width != 2:
        raise SetupError("立体声参考请先转成 16-bit PCM WAV，或安装 ffmpeg 后再跑本命令。")
    sample_count = len(frames) // 2
    if sample_count % channels != 0:
        raise SetupError("WAV 帧长度和声道对不上。")
    out = bytearray()
    for index in range(0, sample_count, channels):
        left = struct.unpack_from("<h", frames, index * 2)[0]
        out.extend(struct.pack("<h", left))
    return bytes(out)


def _write_wav(path: Path, frames: bytes, *, rate: int, width: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(width)
        handle.setframerate(rate)
        handle.writeframes(frames)


def _ffmpeg_convert(source: Path, dest: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SetupError(
            f"{source.suffix} 需要先转成 WAV。请安装 ffmpeg（Mac：brew install ffmpeg），"
            "或用 QuickTime / 录音机导出 16-bit PCM WAV。"
        )
    dest.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-ac",
        "1",
        "-ar",
        str(TARGET_RATE),
        "-c:a",
        "pcm_s16le",
        str(dest),
    ]
    completed = __import__("subprocess").run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0 or not dest.is_file():
        raise SetupError(
            f"ffmpeg 没能把 {source.name} 转成单声道 WAV。请改用录音机直接导出 wav。"
        )


def install_reference(
    source: Path,
    *,
    voice_id: str = DEMO_VOICE_ID,
    dest: Path | None = None,
    force: bool = False,
) -> Path:
    if not source.is_file():
        raise SetupError(
            f"找不到录音文件：{source}。请先自录约 10 秒 WAV，见 tools/tts/voices/local/README.md"
        )
    registry = VoiceRegistry.load()
    voice = registry.by_id(voice_id)
    if voice is None:
        raise SetupError(f"登记里没有 {voice_id}。教学项目用 CV007。")
    target = dest or registry.local_reference_path_for(voice)
    if target.is_file() and not force:
        raise SetupError(
            f"声槽已有参考：{target}。确认要覆盖再加 --force。"
        )

    suffix = source.suffix.lower()
    work = source
    tmp_converted: Path | None = None
    if suffix != ".wav":
        tmp_converted = target.with_name(target.name + ".converting.wav")
        _ffmpeg_convert(source, tmp_converted)
        work = tmp_converted

    channels, rate, duration = _wav_info(work)
    if duration < MIN_SECONDS:
        raise SetupError(
            f"录音只有 {duration:.1f} 秒，太短。请在安静房间重录约 10 秒"
            f"（至少 {MIN_SECONDS:.0f} 秒），照着 registry 参考句读。"
        )
    if duration > MAX_SECONDS:
        raise SetupError(
            f"录音有 {duration:.1f} 秒，太长。截到大约 10 秒再装（上限 {MAX_SECONDS:.0f} 秒）。"
        )

    frames, channels, rate, width = _pcm_frames(work)
    mono = _to_mono_pcm(frames, channels, width)
    _write_wav(target, mono, rate=rate, width=width)
    if tmp_converted is not None:
        tmp_converted.unlink(missing_ok=True)

    notes: list[str] = []
    if channels > 1:
        notes.append("已取左声道变成单声道。")
    if rate != TARGET_RATE:
        notes.append(
            f"采样率是 {rate} Hz（生成时 mlx-audio 会重采样到 {TARGET_RATE}）。"
            "想本机对齐可以：ffmpeg -i 原文件 -ac 1 -ar 24000 -c:a pcm_s16le 新文件.wav"
        )
    if duration < WARN_LOW or duration > WARN_HIGH:
        notes.append(f"时长 {duration:.1f} 秒；建议 8–15 秒，目标约 10 秒。")
    setattr(install_reference, "last_notes", notes)
    return target


def _print_record_tips(voice_id: str) -> None:
    registry = VoiceRegistry.load()
    voice = registry.by_id(voice_id)
    text = registry.reference_text_for(voice) if voice else ""
    print("录音要点：")
    print("  1. 安静房间，关掉风扇 / 音乐 / 空调；手机飞行模式")
    print("  2. 对着嘴约 15–20cm，正常说话，不要喊、不要气声贴麦")
    print("  3. 导出 单声道 16-bit PCM WAV（不要 m4a/mp3 当最终文件）")
    print("  4. 长度约 10 秒（8–15 秒都能用）")
    print("  5. 尽量读准下面这句（和 registry 参考句一致）：")
    if text:
        print(f"     {text}")
    print()
    print("QuickTime：文件 → 新建音频录制 → 停 → 导出为 WAV。")
    print("或：ffmpeg -f avfoundation -i \":0\" -t 10 -ac 1 -ar 24000 -c:a pcm_s16le ~/Desktop/reference.wav")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wav", nargs="?", type=Path, help="你的录音文件（WAV 最好）")
    parser.add_argument("--voice", default=DEMO_VOICE_ID, help=f"声槽 ID（默认 {DEMO_VOICE_ID}）")
    parser.add_argument("--dest", type=Path, help="覆盖默认 local/ 路径（测试用）")
    parser.add_argument("--force", action="store_true", help="覆盖已有参考")
    parser.add_argument("--print-tips", action="store_true", help="只打印录音说明")
    args = parser.parse_args(argv)
    if args.print_tips or args.wav is None:
        _print_record_tips(args.voice)
        if args.wav is None and not args.print_tips:
            print("REFERENCE 安装: FAIL — 请传入录音文件路径。", file=sys.stderr)
            return 2
        if args.wav is None:
            return 0
    try:
        dest = install_reference(
            args.wav.expanduser(),
            voice_id=args.voice,
            dest=args.dest,
            force=args.force,
        )
    except SetupError as error:
        print(f"REFERENCE 安装: FAIL — {error}", file=sys.stderr)
        print("下一步：python3 tools/tts/install_reference.py --print-tips", file=sys.stderr)
        return 2
    print(f"已安装到（gitignore）：{dest}")
    for note in getattr(install_reference, "last_notes", []):
        print(f"注意：{note}")
    print()
    print("下一步：")
    print("  python3 tools/tts/setup_check.py")
    print("  python3 tools/cli.py smoke-narrate")
    print("REFERENCE 安装: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
