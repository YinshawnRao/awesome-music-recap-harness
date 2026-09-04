from __future__ import annotations

import os
from pathlib import Path

import pytest

from tools.cli import COMMANDS
from tools.video.smoke_download import (
    SMOKE_VIDEO_ID,
    SmokeDownloadError,
    cookie_state,
    preflight,
    main as smoke_main,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_JAR = REPO_ROOT / "examples" / "cookies" / "all_cookies.example.txt"


def _install_example(root: Path) -> Path:
    dest = root / "all_cookies.txt"
    dest.write_text(EXAMPLE_JAR.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(dest, 0o600)
    return dest


def test_missing_jar_is_hard_fail(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SmokeDownloadError, match="all_cookies.txt"):
        preflight(tmp_path)
    captured = capsys.readouterr().out
    assert "COOKIE 预检: 缺失" in captured
    assert "install_cookies.sh" in captured
    assert "yt_dlp_readonly.py" in captured


def test_placeholder_warns_but_can_continue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _install_example(tmp_path)
    assert cookie_state(tmp_path / "all_cookies.txt") == "placeholder"
    assert preflight(tmp_path, allow_placeholder=True) == "placeholder"
    captured = capsys.readouterr().out
    assert "COOKIE 预检: 占位符" in captured
    assert "B 站" in captured


def test_strict_cookies_fail_on_placeholder(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _install_example(tmp_path)
    with pytest.raises(SmokeDownloadError, match="占位符"):
        preflight(tmp_path, allow_placeholder=False)
    assert "COOKIE 预检: 占位符" in capsys.readouterr().out


def test_cli_missing_jar_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert smoke_main(["--repo-root", str(tmp_path)]) == 2
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "SMOKE DOWNLOAD: FAIL" in text
    assert "install_cookies.sh" in text
    assert SMOKE_VIDEO_ID in captured.out


def test_cli_dispatcher_exposes_p1_commands() -> None:
    assert "smoke-download" in COMMANDS
    assert "install-cookies" in COMMANDS
    assert "placeholder-clips" in COMMANDS


def test_cli_strict_placeholder_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _install_example(tmp_path)
    assert smoke_main(["--repo-root", str(tmp_path), "--strict-cookies"]) == 2
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "占位符" in text
    assert "SMOKE DOWNLOAD: FAIL" in text
