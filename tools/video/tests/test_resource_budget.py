from __future__ import annotations

from tools.video.resource_budget import (
    FFMPEG_THREADS_ENV,
    _bounded_override,
    _threads_for_count,
)


# resource_budget still exports the renamed constants
def test_adaptive_ladder() -> None:
    assert _threads_for_count(1) == 4
    assert _threads_for_count(2) == 3
    assert _threads_for_count(3) == 2
    assert _threads_for_count(8) == 2


def test_override_bounds() -> None:
    assert _bounded_override({FFMPEG_THREADS_ENV: "2"}, FFMPEG_THREADS_ENV) == 2
    try:
        _bounded_override({FFMPEG_THREADS_ENV: "8"}, FFMPEG_THREADS_ENV)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
