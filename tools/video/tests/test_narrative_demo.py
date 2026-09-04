from __future__ import annotations

import json
from pathlib import Path

from tools.tts.verify_voice_usage import verify_voice_usage
from tools.video.outro_cta import FIXED_OUTRO_CTA
from tools.video.verify_project import verify_project
from tools.video.verify_publishing import verify_publishing

NARRATIVE = Path(__file__).resolve().parents[3] / "examples" / "narrative-eras-demo"


def test_narrative_demo_structure() -> None:
    errors = verify_project(NARRATIVE)
    assert errors == []
    manifest = json.loads((NARRATIVE / "project-manifest.json").read_text(encoding="utf-8"))
    assert manifest["project_kind"] == "narrative"
    assert all("rank" not in item for item in manifest["items"])
    assert len(manifest["items"]) == 3
    cta = next(
        block for block in manifest["narration_sequence"] if block["role"] == "outro_cta"
    )
    assert cta["text"] == FIXED_OUTRO_CTA


def test_narrative_voice_structure() -> None:
    errors, mode = verify_voice_usage(
        NARRATIVE / "voice-selection.json",
        NARRATIVE,
    )
    assert errors == []
    assert mode == "structure"


def test_narrative_publishing_passes() -> None:
    summary = verify_publishing(NARRATIVE)
    assert summary.title_count == 3
    assert 8 <= summary.hashtag_count <= 10
    assert summary.relevance_kind in {"performer", "cover_theme"}


def test_narrative_songs_have_no_rank() -> None:
    songs = json.loads((NARRATIVE / "songs.json").read_text(encoding="utf-8"))
    assert songs["project_kind"] == "narrative"
    assert all("rank" not in song for song in songs["songs"])
