from __future__ import annotations

from tools.tts.text_normalizer import normalize_tts_text


def test_pure_chinese_unchanged() -> None:
    text = "今天只讲北城那些被低估的舞台。"
    result = normalize_tts_text(text)
    assert result.normalized_text == text
    assert result.changed is False


def test_beyond_word_case() -> None:
    result = normalize_tts_text("重听BEYOND的现场。")
    assert "Beyond" in result.normalized_text
    assert "BEYOND" not in result.normalized_text


def test_bts_letterized() -> None:
    result = normalize_tts_text("候选里有BTS。")
    assert "B T S" in result.normalized_text
