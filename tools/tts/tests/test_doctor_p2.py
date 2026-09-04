from __future__ import annotations

from tools.tts.doctor import run_doctor


def test_structure_only_pass_without_weights() -> None:
    code, notes = run_doctor("CV007", require_reference=False)
    assert code == 0
    text = "\n".join(notes)
    assert "PASS structure-only" in text
    assert "voice=CV007" in text


def test_require_reference_fails_closed() -> None:
    code, notes = run_doctor("CV007", require_reference=True)
    assert code == 1
    text = "\n".join(notes)
    assert "reference WAV is required" in text or "TTS DOCTOR: FAIL" in text
    assert "Kokoro" in text
