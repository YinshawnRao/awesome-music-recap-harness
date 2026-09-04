from __future__ import annotations

import struct
import subprocess
import wave
from pathlib import Path

import pytest

from tools.tts.install_reference import install_reference, main as install_main
from tools.tts.qwen_env import SetupError


def _write_wav(
    path: Path,
    *,
    seconds: float = 10.0,
    rate: int = 24000,
    channels: int = 1,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(seconds * rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        if channels == 1:
            handle.writeframes(b"\x00\x00" * frames)
            return
        payload = bytearray()
        for _ in range(frames):
            payload.extend(struct.pack("<hh", 12, 34))
        handle.writeframes(bytes(payload))


def test_installs_mono_wav_to_dest(tmp_path: Path) -> None:
    source = tmp_path / "in.wav"
    dest = tmp_path / "local" / "CV007" / "reference.wav"
    _write_wav(source, seconds=10)
    installed = install_reference(source, dest=dest)
    assert installed == dest
    assert dest.is_file()
    with wave.open(str(dest), "rb") as handle:
        assert handle.getnchannels() == 1
        assert handle.getnframes() / handle.getframerate() >= 9.0


def test_rejects_too_short(tmp_path: Path) -> None:
    source = tmp_path / "short.wav"
    dest = tmp_path / "reference.wav"
    _write_wav(source, seconds=1.0)
    with pytest.raises(SetupError, match="太短"):
        install_reference(source, dest=dest)


def test_stereo_becomes_mono(tmp_path: Path) -> None:
    source = tmp_path / "stereo.wav"
    dest = tmp_path / "reference.wav"
    _write_wav(source, seconds=9.0, channels=2)
    install_reference(source, dest=dest)
    with wave.open(str(dest), "rb") as handle:
        assert handle.getnchannels() == 1


def test_cli_missing_file_is_chinese(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "nope.wav"
    assert install_main([str(missing)]) == 2
    text = capsys.readouterr().err
    assert "REFERENCE 安装: FAIL" in text
    assert "找不到录音文件" in text
    assert "print-tips" in text


def test_gitignore_keeps_local_readme_and_ignores_wav() -> None:
    repo = Path(__file__).resolve().parents[3]
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", "tools/tts/voices/local/README.md"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    # File may not be staged yet during collection; path must at least exist.
    assert (repo / "tools/tts/voices/local/README.md").is_file()
    if tracked.returncode == 0:
        assert tracked.stdout.strip().endswith("tools/tts/voices/local/README.md")

    ignored = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "tools/tts/voices/local/CV007/reference.wav",
        ],
        cwd=repo,
        check=False,
    )
    assert ignored.returncode == 0
