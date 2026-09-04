from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest

from tools.video.check_yt_cookie import (
    REQUIRED,
    REQUIRED_BILIBILI,
    inspect_jar,
    main as check_main,
)
from tools.video.filter_cookie_jar import filter_cookie_jar
from tools.video.yt_dlp_readonly import CookieGuardError, private_cookie_snapshot, run_yt_dlp


REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_JAR = REPO_ROOT / "examples" / "cookies" / "all_cookies.example.txt"


def test_example_jar_is_valid_netscape_with_placeholder_values() -> None:
    text = EXAMPLE_JAR.read_text(encoding="utf-8")
    assert text.startswith("# Netscape HTTP Cookie File")
    inspection = inspect_jar(EXAMPLE_JAR)
    names = {name for _, name, _ in inspection.rows}
    assert set(REQUIRED) <= names
    assert set(REQUIRED_BILIBILI) <= names
    assert inspection.placeholder_values is True
    assert "youtube.com" in text
    assert "google.com" in text
    assert "bilibili.com" in text
    for line in text.splitlines():
        if not line or line.startswith("#") and not line.startswith("#HttpOnly_"):
            continue
        fields = line.removeprefix("#HttpOnly_").split("\t")
        assert len(fields) >= 7
        value = fields[6]
        assert "PLACEHOLDER" in value.upper() or "EXAMPLE" in value.upper()
        assert len(value) < 80


def test_check_fails_placeholder_example(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    installed = tmp_path / "all_cookies.txt"
    installed.write_text(EXAMPLE_JAR.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(installed, 0o600)
    assert check_main([str(installed)]) == 1
    captured = capsys.readouterr().out
    assert "placeholder-value advisory" in captured
    assert "PLACEHOLDER_NOT_A_SESSION" not in captured
    assert "static preflight: FAIL" in captured


def test_check_reports_missing_runtime_jar(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    missing = tmp_path / "all_cookies.txt"
    assert check_main([str(missing)]) == 2
    captured = capsys.readouterr().out
    assert "Cookie file is missing" in captured
    assert "full dual-platform" in captured
    assert "public downloads can continue" not in captured


def test_readonly_snapshot_lives_outside_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    canonical = repo / "all_cookies.txt"
    canonical.write_text(EXAMPLE_JAR.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(canonical, 0o600)
    with private_cookie_snapshot(canonical, repo_root=repo) as snapshot:
        assert snapshot.is_file()
        assert snapshot.name == "cookies.txt"
        assert "amrh-cookie-" in str(snapshot)
        try:
            snapshot.resolve().relative_to(repo.resolve())
            raise AssertionError("snapshot must not live inside the repository")
        except ValueError:
            pass
        assert stat.S_IMODE(snapshot.stat().st_mode) == 0o600


def test_wrapper_requires_canonical_jar(tmp_path: Path) -> None:
    with pytest.raises(CookieGuardError, match="unavailable"):
        run_yt_dlp(
            ["https://example.com/watch", "--skip-download"],
            canonical=tmp_path / "all_cookies.txt",
            repo_root=tmp_path,
        )


def test_filter_accepts_copied_example_outside_repo(tmp_path: Path) -> None:
    source = tmp_path / "raw.txt"
    output = tmp_path / "candidate.txt"
    source.write_text(EXAMPLE_JAR.read_text(encoding="utf-8"), encoding="utf-8")
    os.chmod(source, 0o600)
    result = filter_cookie_jar(source, output=output, repo_root=REPO_ROOT)
    assert result.retained >= 10
    assert output.is_file()
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
    inspection = inspect_jar(output)
    names = {name for _, name, _ in inspection.rows}
    assert set(REQUIRED) <= names
    assert set(REQUIRED_BILIBILI) <= names


def test_gitignore_keeps_example_and_ignores_runtime_jar() -> None:
    tracked = subprocess.run(
        ["git", "add", "-n", "--", "examples/cookies/all_cookies.example.txt"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert tracked.returncode == 0
    assert "all_cookies.example.txt" in tracked.stdout + tracked.stderr

    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "--", "all_cookies.txt"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert ignored.returncode == 0

    also_ignored = subprocess.run(
        ["git", "check-ignore", "-q", "--", "cookies.txt"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert also_ignored.returncode == 0
