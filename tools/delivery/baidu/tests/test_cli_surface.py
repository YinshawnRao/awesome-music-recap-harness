from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.cli import COMMANDS, main as cli_main

REPO = Path(__file__).resolve().parents[4]


def test_cli_exposes_baidu_upload() -> None:
    assert "baidu-upload" in COMMANDS
    assert COMMANDS["baidu-upload"].name == "upload.py"


def test_cli_help_lists_baidu(capsys) -> None:
    try:
        cli_main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    text = capsys.readouterr().out
    assert "baidu-upload" in text
    assert "dry-run" in text


def test_baidu_upload_help_is_chinese() -> None:
    completed = subprocess.run(
        [sys.executable, str(REPO / "tools" / "cli.py"), "baidu-upload", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    text = completed.stdout
    assert "--dry-run" in text
    assert "只上传" in text
    assert "AMRH_BAIDU" in text
    assert "仓库外" in text


def test_baidu_dry_run_without_token(tmp_path: Path, capsys, monkeypatch) -> None:
    from tools.delivery.baidu.upload import main as baidu_main

    local = tmp_path / "note.md"
    local.write_text("ok\n", encoding="utf-8")
    monkeypatch.delenv("AMRH_BAIDU_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("AMRH_BAIDU_CREDENTIALS_FILE", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "baidu-upload",
            "--dry-run",
            "--local",
            str(local),
            "--remote",
            "/apps/amrh/note.md",
        ],
    )
    assert baidu_main() == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "BAIDU UPLOAD: DRY-RUN" in text
    assert "access_token" not in text
    assert "凭证" in text
