from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path

from tools.cli import COMMANDS
from tools.video.mix_master import mix_master, write_bed
from tools.video.render_host import HostReport, inspect_render_host
from tools.video.smoke_e2e import (
    COMPOSITION_FILES,
    CLIP_RELS,
    assert_composition_files,
    main as smoke_main,
)


REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "examples" / "top-ranking-demo"


def test_cli_dispatcher_exposes_p3_commands() -> None:
    assert "smoke-e2e" in COMMANDS
    assert "mix-master" in COMMANDS
    assert "placeholder-clips" in COMMANDS


def test_demo_composition_is_committed_vertical_n_to_1() -> None:
    assert_composition_files(DEMO)
    html = (DEMO / "index.html").read_text(encoding="utf-8")
    css = (DEMO / "styles.css").read_text(encoding="utf-8")
    package = json.loads((DEMO / "package.json").read_text(encoding="utf-8"))
    timeline = json.loads((DEMO / "smoke-timeline.json").read_text(encoding="utf-8"))
    assert html.count("vert_rank-0") >= 5
    assert 'data-width="1080"' in html
    assert 'data-height="1920"' in html
    assert 'data-duration="30"' in html
    assert "05→01" not in html
    assert "N→1" not in html
    assert "倒数开始" not in html
    assert "fonts.googleapis.com" not in css
    assert "fonts.googleapis.com" not in html
    assert package["devDependencies"]["hyperframes"] == "0.6.69"
    assert "hyperframes@0.6.69" in package["scripts"]["render"]
    assert "--sdr" in package["scripts"]["render"]
    ranks = [section["rank"] for section in timeline["sections"] if section.get("rank")]
    assert ranks == [5, 4, 3, 2, 1]
    assert timeline["duration"] == 30
    assert timeline["hyperframes"] == "0.6.69"
    cover = timeline["sections"][0]
    assert cover["role"] == "cover"
    assert cover["clip"].endswith("vert_rank-05.mp4")


def test_gitignore_keeps_html_and_drops_mp4() -> None:
    ignored_mp4 = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "examples/top-ranking-demo/renders/top-ranking-demo.mp4",
        ],
        cwd=REPO,
        check=False,
    )
    assert ignored_mp4.returncode == 0
    ignored_wav = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "examples/top-ranking-demo/master.wav",
        ],
        cwd=REPO,
        check=False,
    )
    assert ignored_wav.returncode == 0
    tracked_html = subprocess.run(
        [
            "git",
            "check-ignore",
            "-q",
            "--",
            "examples/top-ranking-demo/index.html",
        ],
        cwd=REPO,
        check=False,
    )
    assert tracked_html.returncode == 1


def test_structure_only_passes_without_chrome(capsys) -> None:
    code = smoke_main(["--project", str(DEMO), "--structure-only"])
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert code == 0
    assert "SMOKE E2E: PASS structure-only" in text


def test_missing_chrome_prints_chinese_next_steps(monkeypatch, capsys) -> None:
    def _no_chrome_host(**_kwargs):
        return HostReport(ok=False, missing=["Chrome / Chromium（HyperFrames 渲染用）"])

    monkeypatch.setattr("tools.video.smoke_e2e.inspect_render_host", _no_chrome_host)
    code = smoke_main(["--project", str(DEMO), "--check-only", "--skip-gates"])
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert code == 2
    assert "SMOKE E2E: FAIL" in text
    assert "Chrome" in text
    assert "brew install ffmpeg" in text
    assert "hyperframes@0.6.69" in text
    assert "@latest" in text


def test_inspect_render_host_can_fail_closed() -> None:
    report = inspect_render_host(which=lambda _name: None, chrome_path="")
    assert report.ok is False
    assert "ffmpeg" in " ".join(report.missing)
    assert "Chrome" in report.chinese_next_steps()
    assert "smoke-e2e" in report.chinese_next_steps()


def test_mix_master_silent_bed(tmp_path: Path) -> None:
    timeline = json.loads((DEMO / "smoke-timeline.json").read_text(encoding="utf-8"))
    (tmp_path / "smoke-timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False), encoding="utf-8"
    )
    path, mode = mix_master(tmp_path, dest=tmp_path / "master.wav")
    assert mode == "silent"
    assert path.is_file()
    with wave.open(str(path), "r") as handle:
        assert handle.getnchannels() == 2
        assert handle.getframerate() == 48000
        seconds = handle.getnframes() / handle.getframerate()
    assert 29.5 <= seconds <= 30.5


def test_mix_master_tone_bed(tmp_path: Path) -> None:
    timeline = json.loads((DEMO / "smoke-timeline.json").read_text(encoding="utf-8"))
    (tmp_path / "smoke-timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False), encoding="utf-8"
    )
    path, mode = mix_master(tmp_path, dest=tmp_path / "master.wav", tone=True)
    assert mode == "tone"
    with wave.open(str(path), "r") as handle:
        frames = handle.readframes(min(handle.getnframes(), 4800))
    assert any(byte != 0 for byte in frames)


def test_write_bed_duration() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as raw:
        dest = Path(raw) / "bed.wav"
        write_bed(dest, 0.25, tone=False)
        with wave.open(str(dest), "r") as handle:
            assert handle.getnframes() == 12000


def test_composition_file_list_is_complete() -> None:
    for name in COMPOSITION_FILES:
        assert (DEMO / name).is_file(), name
    for rel in CLIP_RELS:
        assert rel.startswith("clips/vert_rank-")
