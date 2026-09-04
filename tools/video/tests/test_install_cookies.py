from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from tools.video.check_yt_cookie import inspect_jar
from tools.video.install_cookies import (
    InstallCookiesError,
    install_example_jar,
    jar_state,
    main as install_main,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_JAR = REPO_ROOT / "examples" / "cookies" / "all_cookies.example.txt"


def test_copies_example_and_sets_0600(tmp_path: Path) -> None:
    dest = tmp_path / "all_cookies.txt"
    path, action = install_example_jar(repo_root=REPO_ROOT, dest=dest)
    assert action == "copied"
    assert path == dest
    assert dest.is_file()
    assert stat.S_IMODE(dest.stat().st_mode) == 0o600
    assert inspect_jar(dest).placeholder_values is True
    assert jar_state(dest) == "placeholder"


def test_does_not_overwrite_ready_jar(tmp_path: Path) -> None:
    dest = tmp_path / "all_cookies.txt"
    text = (
        EXAMPLE_JAR.read_text(encoding="utf-8")
        .replace("PLACEHOLDER_NOT_A_SESSION", "LIVESESSIONTOKEN")
        .replace("PLACEHOLDER_EXAMPLE", "LIVEUSERID")
    )
    dest.write_text(text, encoding="utf-8")
    os.chmod(dest, 0o600)
    before = dest.read_text(encoding="utf-8")
    path, action = install_example_jar(repo_root=REPO_ROOT, dest=dest)
    assert action == "already-ready"
    assert path == dest
    assert dest.read_text(encoding="utf-8") == before


def test_keeps_existing_placeholder(tmp_path: Path) -> None:
    dest = tmp_path / "all_cookies.txt"
    dest.write_text(EXAMPLE_JAR.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(dest, 0o644)
    _, action = install_example_jar(repo_root=REPO_ROOT, dest=dest)
    assert action == "already-placeholder"
    assert stat.S_IMODE(dest.stat().st_mode) == 0o600


def test_cli_prints_next_steps_without_secrets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dest = tmp_path / "all_cookies.txt"
    assert install_main(["--dest", str(dest), "--repo-root", str(REPO_ROOT)]) == 0
    captured = capsys.readouterr().out
    assert "COOKIE 安装: OK" in captured
    assert "filter_cookie_jar.py" in captured
    assert "PLACEHOLDER_NOT_A_SESSION_sid" not in captured
    assert dest.is_file()


def test_missing_template_fails(tmp_path: Path) -> None:
    with pytest.raises(InstallCookiesError, match="格式模板"):
        install_example_jar(repo_root=tmp_path, dest=tmp_path / "all_cookies.txt")
