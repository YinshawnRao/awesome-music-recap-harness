from __future__ import annotations

from pathlib import Path

from tools.video.verify_publishing import verify_publishing

DEMO = Path(__file__).resolve().parents[3] / "examples" / "top-ranking-demo"


def test_demo_publishing_passes() -> None:
    summary = verify_publishing(DEMO)
    assert summary.title_count == 3
    assert 8 <= summary.hashtag_count <= 10
    assert summary.relevance_kind in {"performer", "cover_theme"}


def test_prose_length_in_range() -> None:
    text = (DEMO / "publishing" / "xiaohongshu.md").read_text(encoding="utf-8")
    body = text.split("## 正文", 1)[1]
    prose = "\n".join(line for line in body.splitlines() if line.strip() and not line.strip().startswith("#"))
    # last non-empty line is hashtags; drop it
    lines = [line for line in body.splitlines() if line.strip()]
    prose_lines = lines[:-1]
    prose = "\n".join(prose_lines)
    count = sum(not character.isspace() for character in prose)
    assert 420 <= count <= 900, count
