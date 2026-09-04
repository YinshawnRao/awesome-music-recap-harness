from __future__ import annotations

from pathlib import Path

import pytest

from tools.delivery.baidu.upload import (
    CredentialError,
    load_credentials,
    md5_blocks,
    normalize_remote,
    plan_upload,
)


def test_normalize_remote() -> None:
    assert normalize_remote("shows/a.mp4", "amrh") == "/apps/amrh/shows/a.mp4"
    assert normalize_remote("/apps/amrh/x.mp4", "amrh") == "/apps/amrh/x.mp4"


def test_md5_blocks_emptyish(tmp_path: Path) -> None:
    path = tmp_path / "tiny.bin"
    path.write_bytes(b"hello")
    blocks = md5_blocks(path)
    assert len(blocks) == 1
    assert len(blocks[0]) == 32


def test_credentials_missing() -> None:
    with pytest.raises(CredentialError):
        load_credentials(environ={})


def test_dry_run_plan(tmp_path: Path) -> None:
    local = tmp_path / "clip.mp4"
    local.write_bytes(b"0" * 16)
    plan = plan_upload(local, "demo.mp4", None)
    assert plan["steps"] == ["precreate", "superfile2", "create"]
    assert plan["has_token"] is False
    assert plan["remote"].startswith("/apps/")
