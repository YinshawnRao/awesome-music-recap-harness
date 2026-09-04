from __future__ import annotations

import subprocess
from pathlib import Path

from tools.cli import COMMANDS
from tools.tts.qwen_env import (
    KOKORO_BAN,
    SetupError,
    inspect_setup,
    require_generation_ready,
)
from tools.tts.setup_check import main as setup_main
from tools.tts.voice_registry import VoiceRegistry


def test_linux_setup_fails_closed_in_chinese(
    capsys, monkeypatch
) -> None:
    monkeypatch.delenv("AMRH_QWEN_PYTHON", raising=False)
    monkeypatch.delenv("AMRH_QWEN_BASE_MODEL", raising=False)
    assert setup_main(["--voice", "CV007", "--skip-mlx-import"]) == 2
    text = capsys.readouterr().err
    assert "TTS SETUP: FAIL" in text
    assert "Apple Silicon" in text
    assert "AMRH_QWEN_PYTHON" in text
    assert "AMRH_QWEN_BASE_MODEL" in text
    assert "权重不随仓库分发" in text
    assert "Kokoro" in text
    assert "install_reference.py" in text


def test_inspect_setup_can_pass_when_runtime_is_injected(
    tmp_path: Path, monkeypatch
) -> None:
    python_bin = tmp_path / "qwen-python"
    python_bin.write_text("#!/bin/sh\n", encoding="utf-8")
    python_bin.chmod(0o755)
    model = tmp_path / "model"
    model.mkdir()
    (model / "config.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("AMRH_QWEN_PYTHON", str(python_bin))
    monkeypatch.setenv("AMRH_QWEN_BASE_MODEL", str(model))

    registry = VoiceRegistry.load()
    voice = registry.by_id("CV007")
    assert voice is not None
    reference = tmp_path / "ref.wav"
    reference.write_bytes(b"RIFF")
    monkeypatch.setattr(
        VoiceRegistry,
        "reference_path_for",
        lambda self, _voice: reference,
    )

    report = inspect_setup(
        "CV007",
        registry=registry,
        platform_name="darwin",
        machine_name="arm64",
        metal_checker=lambda: True,
        check_mlx_import=False,
    )
    assert report.ok is True
    assert report.qwen_python == str(python_bin)
    assert report.qwen_model == str(model)


def test_require_generation_ready_rejects_missing_runtime() -> None:
    try:
        require_generation_ready("CV007", check_mlx_import=False)
    except SetupError as error:
        text = str(error)
        assert "TTS SETUP: FAIL" in text
        assert KOKORO_BAN in text
        assert "docs/mac-setup.md" in text or "bootstrap_mac.sh" in text
    else:
        raise AssertionError("expected SetupError")


def test_bootstrap_script_fails_closed_on_linux() -> None:
    script = Path(__file__).resolve().parents[1] / "bootstrap_mac.sh"
    completed = subprocess.run(
        ["bash", str(script)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    text = completed.stdout + completed.stderr
    assert "TTS BOOTSTRAP: FAIL" in text
    assert "Kokoro" in text
    assert "mac-setup.md" in text


def test_cli_exposes_p2_commands() -> None:
    assert "smoke-narrate" in COMMANDS
    assert "tts-setup" in COMMANDS
    assert "install-reference" in COMMANDS
