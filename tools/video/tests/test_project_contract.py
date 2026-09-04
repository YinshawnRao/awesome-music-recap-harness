from __future__ import annotations

import json
from pathlib import Path

from tools.video.outro_cta import FIXED_OUTRO_CTA
from tools.video.verify_project import verify_project

DEMO = Path(__file__).resolve().parents[3] / "examples" / "top-ranking-demo"
NARRATIVE = Path(__file__).resolve().parents[3] / "examples" / "narrative-eras-demo"


def test_flagship_demo_structure() -> None:
    errors = verify_project(DEMO)
    assert errors == []


def test_narrative_scaffold_is_not_top_ranking() -> None:
    errors = verify_project(NARRATIVE)
    assert errors == []
    manifest = json.loads((NARRATIVE / "project-manifest.json").read_text(encoding="utf-8"))
    assert manifest["project_kind"] == "narrative"


def test_top_order_must_be_n_to_1(tmp_path: Path) -> None:
    manifest = json.loads((DEMO / "project-manifest.json").read_text(encoding="utf-8"))
    manifest["items"] = list(reversed(manifest["items"]))
    (tmp_path / "project-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (tmp_path / "voice-selection.json").write_text("{}", encoding="utf-8")
    for block in manifest["narration_sequence"]:
        sidecar = tmp_path / block["sidecar"]
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text("{}", encoding="utf-8")
    errors = verify_project(tmp_path)
    assert any("N→1" in error for error in errors)


def test_cta_must_match() -> None:
    assert "投票" in FIXED_OUTRO_CTA
    manifest = json.loads((DEMO / "project-manifest.json").read_text(encoding="utf-8"))
    cta = next(block for block in manifest["narration_sequence"] if block["role"] == "outro_cta")
    assert cta["text"] == FIXED_OUTRO_CTA
