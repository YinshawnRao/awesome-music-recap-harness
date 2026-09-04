from __future__ import annotations

from tools.tts.voice_registry import VoiceRegistry, resolve_selector, resolve_task_prompt


def test_registry_loads_ten_voice_pool() -> None:
    registry = VoiceRegistry.load()
    assert registry.preflight_id == "CV001"
    assert len(registry.decision_pool_ids) == 10
    assert registry.decision_pool_ids == registry.random_pool_ids


def test_explicit_selector() -> None:
    registry = VoiceRegistry.load()
    selection = resolve_selector(registry, "CV007")
    assert selection["resolved_voice_id"] == "CV007"
    assert selection["selection_mode"] == "explicit"
    assert selection["fallback"] is False


def test_model_decision_from_brief() -> None:
    registry = VoiceRegistry.load()
    selection = resolve_task_prompt(
        registry,
        "做一个被低估现场盘点",
        model_choice="CV007",
        model_reason="Archival documentary tone.",
        model_confidence="high",
    )
    assert selection["resolved_voice_id"] == "CV007"
    assert selection["selection_mode"] == "model_decision"


def test_negative_clause_does_not_select() -> None:
    registry = VoiceRegistry.load()
    selection = resolve_task_prompt(
        registry,
        "不要使用 CV004\n配音：CV006",
        model_choice="CV007",
        model_reason="unused",
        model_confidence="high",
    )
    assert selection["resolved_voice_id"] == "CV006"
    assert selection["selection_mode"] == "explicit"
