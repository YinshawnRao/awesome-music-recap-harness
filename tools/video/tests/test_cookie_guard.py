from __future__ import annotations

from pathlib import Path

import pytest

from tools.video.yt_dlp_readonly import CookieGuardError, _validate_yt_dlp_arguments


def test_rejects_cookie_flags() -> None:
    canonical = Path("/tmp/all_cookies.txt")
    with pytest.raises(CookieGuardError):
        _validate_yt_dlp_arguments(["--cookies", "x"], canonical)


def test_accepts_plain_url() -> None:
    canonical = Path("/tmp/all_cookies.txt")
    safe = _validate_yt_dlp_arguments(["https://example.com/watch", "--skip-download"], canonical)
    assert safe[0].startswith("https://")
