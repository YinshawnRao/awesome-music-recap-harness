from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.tts.narrate import main as narrate_main
from tools.tts.qwen_generate import preflight_metal
from tools.tts.qwen_env import SetupError
from tools.tts.smoke_narrate import main as smoke_main
from tools.tts.verify_voice_usage import verify_voice_usage


REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "examples" / "top-ranking-demo"


def test_smoke_check_only_exits_2_on_linux(capsys) -> None:
    code = smoke_main(["--project", str(DEMO), "--check-only"])
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert code == 2
    assert "TTS SETUP: FAIL" in text
    assert "不要改用 Kokoro" in text
    assert "bootstrap_mac.sh" in text or "mac-setup.md" in text


def test_real_narrate_does_not_silently_dry_run(tmp_path: Path, capsys) -> None:
    output = tmp_path / "out.wav"
    # narrate.main reads sys.argv
    import sys

    old = sys.argv
    sys.argv = [
        "narrate.py",
        "配音烟雾。这是一句很短的测试。",
        "--voice",
        "CV007",
        "-o",
        str(output),
    ]
    try:
        code = narrate_main()
    finally:
        sys.argv = old
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert code == 2
    assert not output.is_file()
    assert "NARRATE: PASS dry-run" not in text
    assert "Kokoro" in text
    assert "TTS SETUP: FAIL" in text


def test_dry_run_still_writes_sidecar_only(tmp_path: Path, capsys) -> None:
    output = tmp_path / "out.wav"
    import sys

    old = sys.argv
    sys.argv = [
        "narrate.py",
        "配音烟雾。这是一句很短的测试。",
        "--voice",
        "CV007",
        "-o",
        str(output),
        "--dry-run",
    ]
    try:
        code = narrate_main()
    finally:
        sys.argv = old
    assert code == 0
    sidecar = output.with_name(output.name + ".tts.json")
    assert sidecar.is_file()
    assert not output.is_file()
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["dry_run"] is True
    assert payload["resolved_voice_id"] == "CV007"
    assert "NARRATE: PASS dry-run" in capsys.readouterr().out


def test_voice_gate_structure_mode_for_demo() -> None:
    errors, mode = verify_voice_usage(
        DEMO / "voice-selection.json",
        DEMO,
        require_wav=False,
    )
    assert errors == []
    assert mode == "structure"


def test_qwen_worker_refuses_without_metal() -> None:
    try:
        preflight_metal()
    except SetupError as error:
        assert "Metal" in str(error)
        assert "Kokoro" in str(error)
    else:
        # Apple Silicon CI would pass; Linux must fail.
        import sys

        if sys.platform != "darwin":
            raise AssertionError("Linux worker must fail closed before MLX import")


def test_gitignore_demo_smoke_wav() -> None:
    ignored = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "examples/top-ranking-demo/audio/smoke.wav",
        ],
        cwd=REPO,
        check=False,
    )
    assert ignored.returncode == 0
    readme = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "examples/top-ranking-demo/audio/README.md",
        ],
        cwd=REPO,
        check=False,
    )
    assert readme.returncode == 1
