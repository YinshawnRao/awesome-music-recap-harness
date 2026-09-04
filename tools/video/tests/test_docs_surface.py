from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def test_roadmap_is_gone() -> None:
    assert not (REPO / "ROADMAP.md").exists()
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    docs_index = (REPO / "docs" / "README.md").read_text(encoding="utf-8")
    assert "ROADMAP.md" not in readme
    assert "ROADMAP.md" not in docs_index
    assert "## 当前能力" in readme


def test_ci_workflow_is_structure_only() -> None:
    workflow = (REPO / ".github" / "workflows" / "structure-gates.yml").read_text(
        encoding="utf-8"
    )
    assert "python3 -m pytest" in workflow
    assert "smoke-e2e -- --structure-only" in workflow
    assert "baidu-upload -- --dry-run" in workflow
    assert "narrative-eras-demo" in workflow
    assert "chrome" not in workflow.lower()
    assert "qwen" not in workflow.lower()
