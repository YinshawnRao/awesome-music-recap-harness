#!/usr/bin/env python3
"""P3 成片烟雾：占位竖屏 +（可选）旁白 → HyperFrames 0.6.69 --sdr → mux。

一条命令走完教学项目的视觉闭环。没有 Qwen / 没有旁白 WAV 时，用静音或
轻正弦床，仍然产出可播放的竖屏 mp4（画面可以是色条）。

Linux CI 常常没有 Chrome：检测后用中文写出下一步并失败，但仓库里的
HTML / CSS / JS / package.json 已经齐，Mac 用户可以直接渲。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


_SCRIPT_DIR = str(Path(__file__).resolve().parent)
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from make_placeholder_clips import PlaceholderClipError, generate_placeholder_clips
from mix_master import MixMasterError, mix_master
from render_host import PINNED_HYPERFRAMES, HostReport, inspect_render_host
from resource_budget import resolve_ffmpeg_threads, resolve_hyperframes_workers


DEFAULT_PROJECT = REPO_ROOT / "examples" / "top-ranking-demo"
COMPOSITION_FILES = (
    "index.html",
    "styles.css",
    "composition.js",
    "package.json",
    "hyperframes.json",
    "smoke-timeline.json",
    "project-manifest.json",
)
CLIP_RELS = (
    "clips/vert_rank-05.mp4",
    "clips/vert_rank-04.mp4",
    "clips/vert_rank-03.mp4",
    "clips/vert_rank-02.mp4",
    "clips/vert_rank-01.mp4",
)


class SmokeE2EError(RuntimeError):
    """User-actionable smoke failure."""


def _run_python(script: Path, args: list[str]) -> int:
    command = [sys.executable, str(script), *args]
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


def assert_composition_files(project: Path) -> None:
    missing = [name for name in COMPOSITION_FILES if not (project / name).is_file()]
    if missing:
        raise SmokeE2EError("合成文件不齐：" + "、".join(missing))
    package = (project / "package.json").read_text(encoding="utf-8")
    if f"hyperframes@{PINNED_HYPERFRAMES}" not in package:
        raise SmokeE2EError(f"package.json 必须锁 hyperframes@{PINNED_HYPERFRAMES}")
    html = (project / "index.html").read_text(encoding="utf-8")
    if 'data-width="1080"' not in html or 'data-height="1920"' not in html:
        raise SmokeE2EError("index.html 必须是竖屏 1080×1920")
    for rel in CLIP_RELS:
        if rel not in html:
            raise SmokeE2EError(f"index.html 应引用 {rel}")


def _clip_duration_seconds(path: Path) -> float:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        return float((completed.stdout or "").strip())
    except ValueError:
        return 0.0


def ensure_placeholder_clips(project: Path) -> None:
    missing = [rel for rel in CLIP_RELS if not (project / rel).is_file()]
    too_short = [
        rel
        for rel in CLIP_RELS
        if (project / rel).is_file() and _clip_duration_seconds(project / rel) < 3.5
    ]
    if not missing and not too_short:
        print("占位竖屏：已存在，跳过生成", flush=True)
        print("vfill：跳过 — P1 占位已经是 1080×1920，不必加黑边", flush=True)
        return
    if too_short:
        print(
            "占位竖屏：时长不够（旧版短鸣曾把片子截成 0.25s），重新生成 4 秒",
            flush=True,
        )
    else:
        print("占位竖屏：缺失，正在生成本机色条 / 色块（不联网）", flush=True)
    generate_placeholder_clips(project, seconds=4, beep=True)
    still = [rel for rel in CLIP_RELS if not (project / rel).is_file()]
    if still:
        raise SmokeE2EError("占位竖屏生成后仍缺：" + "、".join(still))
    print("vfill：跳过 — 占位已经是 1080×1920", flush=True)


def run_structure_gates(project: Path) -> int:
    steps = [
        (
            REPO_ROOT / "tools" / "tts" / "verify_voice_usage.py",
            [
                "--selection",
                str(project / "voice-selection.json"),
                "--project-root",
                str(project),
            ],
        ),
        (
            REPO_ROOT / "tools" / "video" / "verify_project.py",
            ["--project", str(project)],
        ),
        (
            REPO_ROOT / "tools" / "video" / "countdown_build.py",
            ["--project", str(project), "--plan-only"],
        ),
        (
            REPO_ROOT / "tools" / "video" / "verify_publishing.py",
            ["--project", str(project)],
        ),
        (
            REPO_ROOT / "tools" / "video" / "prepare_final_qa.py",
            ["--project", str(project)],
        ),
    ]
    worst = 0
    for script, args in steps:
        code = _run_python(script, args)
        if code != 0:
            worst = code
    return worst


def mux_final(project: Path, render: Path, master: Path, final: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SmokeE2EError("找不到 ffmpeg，无法 mux。Mac：brew install ffmpeg。")
    final.parent.mkdir(parents=True, exist_ok=True)
    lease = resolve_ffmpeg_threads()
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-threads",
        str(lease.threads),
        "-i",
        str(render),
        "-i",
        str(master),
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(final),
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as error:
        raise SmokeE2EError(f"无法启动 ffmpeg mux：{error}") from error
    finally:
        lease.close()
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip().splitlines()
        hint = detail[-1] if detail else f"exit {completed.returncode}"
        raise SmokeE2EError(f"mux 失败：{hint}")


def render_hyperframes(project: Path, output: Path, *, quality: str) -> None:
    npx = shutil.which("npx")
    if not npx:
        raise SmokeE2EError("找不到 npx。先装 Node 22+。")
    output.parent.mkdir(parents=True, exist_ok=True)
    lease = resolve_hyperframes_workers()
    env = os.environ.copy()
    env["HYPERFRAMES_NO_UPDATE_CHECK"] = "1"
    env["HYPERFRAMES_SKIP_SKILLS"] = "1"
    command = [
        npx,
        "--yes",
        f"hyperframes@{PINNED_HYPERFRAMES}",
        "render",
        str(project),
        "--output",
        str(output),
        "--sdr",
        "--quality",
        quality,
        "--workers",
        str(lease.threads),
    ]
    print(
        f"渲染：hyperframes@{PINNED_HYPERFRAMES} --sdr --quality {quality} "
        f"--workers {lease.threads}",
        flush=True,
    )
    try:
        completed = subprocess.run(command, check=False, cwd=str(project), env=env)
    finally:
        lease.close()
    if completed.returncode != 0:
        raise SmokeE2EError(
            f"HyperFrames 渲染失败（exit {completed.returncode}）。"
            f"先在项目目录跑：npx --yes hyperframes@{PINNED_HYPERFRAMES} lint"
        )
    if not output.is_file():
        raise SmokeE2EError(f"渲染结束但没有 {output}")


def _print_host(report: HostReport) -> None:
    print(
        f"渲染宿主：node={'ok' if report.node_ok else '缺'} "
        f"ffmpeg={'ok' if report.ffmpeg else '缺'} "
        f"chrome={'ok' if report.chrome else '缺'}",
        flush=True,
    )


def run_smoke(
    project: Path,
    *,
    tone: bool = False,
    quality: str = "draft",
    check_only: bool = False,
    structure_only: bool = False,
    skip_gates: bool = False,
) -> int:
    print("SMOKE E2E — 占位竖屏 + HyperFrames 0.6.69 --sdr → mux", flush=True)
    try:
        assert_composition_files(project)
    except SmokeE2EError as error:
        print(f"SMOKE E2E: FAIL — {error}")
        return 2

    if structure_only:
        if not skip_gates:
            gates = run_structure_gates(project)
            if gates != 0:
                print("SMOKE E2E: FAIL — 结构门禁没过")
                return gates
        print("SMOKE E2E: PASS structure-only（尚未渲染；FINAL 仍是骨架）")
        return 0

    host = inspect_render_host()
    _print_host(host)
    if not host.ok:
        print(host.chinese_next_steps())
        if not skip_gates:
            print("结构门禁仍会跑（不证明成片）：", flush=True)
            run_structure_gates(project)
        return 2

    if check_only:
        if not skip_gates:
            gates = run_structure_gates(project)
            if gates != 0:
                print("SMOKE E2E: FAIL — 结构门禁没过")
                return gates
        print("SMOKE E2E: PASS check-only（宿主能渲，尚未出片）")
        return 0

    try:
        ensure_placeholder_clips(project)
        master, audio_mode = mix_master(project, tone=tone)
        print(f"MIX MASTER: PASS mode={audio_mode} → {master}", flush=True)
        render = project / "renders" / "full.mp4"
        render_hyperframes(project, render, quality=quality)
        slug = "top-ranking-demo"
        songs = project / "songs.json"
        if songs.is_file():
            import json

            payload = json.loads(songs.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and payload.get("slug"):
                slug = str(payload["slug"])
        final = project / "renders" / f"{slug}.mp4"
        mux_final(project, render, master, final)
    except (SmokeE2EError, MixMasterError, PlaceholderClipError, OSError) as error:
        print(f"SMOKE E2E: FAIL — {error}")
        return 2

    if not skip_gates:
        gates = run_structure_gates(project)
        if gates != 0:
            print("SMOKE E2E: FAIL — 成片已写出，但结构门禁没过")
            return gates

    print(f"SMOKE E2E: PASS final={final}")
    print("这是可播放的竖屏烟雾成片。画面可以是色条。FINAL 仍是待审骨架。")
    if audio_mode != "wav":
        print("本片用了占位音轨（静音或轻正弦），不是 P2 真配音，不要当发布成片。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=DEFAULT_PROJECT,
        help="项目目录（默认：examples/top-ranking-demo）",
    )
    parser.add_argument(
        "--tone",
        action="store_true",
        help="没有旁白 WAV 时铺轻正弦床，而不是静音",
    )
    parser.add_argument(
        "--quality",
        choices=("draft", "standard", "high"),
        default="draft",
        help="HyperFrames 质量（烟雾默认 draft）",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="只体检宿主 + 结构，不渲染",
    )
    parser.add_argument(
        "--structure-only",
        action="store_true",
        help="只验已提交的合成文件和门禁，不要求 Chrome",
    )
    parser.add_argument(
        "--skip-gates",
        action="store_true",
        help="跳过四道结构门禁（调试用）",
    )
    args = parser.parse_args(argv)
    return run_smoke(
        args.project.resolve(),
        tone=args.tone,
        quality=args.quality,
        check_only=args.check_only,
        structure_only=args.structure_only,
        skip_gates=args.skip_gates,
    )


if __name__ == "__main__":
    raise SystemExit(main())
