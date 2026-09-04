from __future__ import annotations

import json
from pathlib import Path

from tools.video.countdown_build import load_songs, plan_timeline

DEMO = Path(__file__).resolve().parents[3] / "examples" / "top-ranking-demo"


def test_plan_is_n_to_1() -> None:
    config = load_songs(DEMO / "songs.json")
    timeline = plan_timeline(config, DEMO)
    ranks = [block["rank"] for block in timeline["blocks"]]
    assert ranks == [5, 4, 3, 2, 1]
    assert timeline["hyperframes"] == "0.6.69"
    assert timeline["total_seconds"] > 100
    assert "master.wav" in timeline["mux"]["command"]
