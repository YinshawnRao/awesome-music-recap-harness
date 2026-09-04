#!/usr/bin/env python3
"""Detect whether this host can render hyperframes@0.6.69 --sdr.

Linux CI often has Node/ffmpeg but no Chrome. Mac with brew + Node 22 + Chrome
can render. Doctor ``ok`` is ignored: pinning 0.6.69 makes doctor report an
upgrade to a newer version, which we must not follow.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Sequence


PINNED_HYPERFRAMES = "0.6.69"
MIN_NODE_MAJOR = 22

CHROME_NAMES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
)

MAC_CHROME_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
)


Which = Callable[[str], str | None]


@dataclass
class HostReport:
    ok: bool
    node: str | None = None
    node_ok: bool = False
    npx: str | None = None
    ffmpeg: str | None = None
    chrome: str | None = None
    missing: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def chinese_next_steps(self) -> str:
        missing = "、".join(self.missing) if self.missing else "未知依赖"
        lines = [
            f"SMOKE E2E: FAIL — 本机不能渲染 HyperFrames {PINNED_HYPERFRAMES} 成片。",
            f"缺了：{missing}",
            "",
            "Linux CI 只保证项目结构齐（HTML / CSS / JS / package.json 已提交）。",
            "成片请在装了 Homebrew + Node 22 + Chrome 的 Mac 上跑：",
            "",
            "  brew install ffmpeg",
            "  node -v          # 需要 v22 或更新",
            f"  npx --yes hyperframes@{PINNED_HYPERFRAMES} doctor",
            "  python3 tools/cli.py smoke-e2e",
            "",
            f"只用 hyperframes@{PINNED_HYPERFRAMES}，不要 @latest。渲染必须加 --sdr。",
        ]
        return "\n".join(lines)


def _node_major(version: str) -> int | None:
    match = re.search(r"v?(\d+)", version)
    if not match:
        return None
    return int(match.group(1))


def find_chrome(*, which: Which = shutil.which) -> str | None:
    for name in CHROME_NAMES:
        path = which(name)
        if path:
            return path
    for candidate in MAC_CHROME_PATHS:
        if Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def inspect_render_host(
    *,
    which: Which = shutil.which,
    chrome_path: str | None = None,
) -> HostReport:
    report = HostReport(ok=False)
    node = which("node")
    report.node = node
    if node:
        try:
            raw = subprocess.run(
                [node, "-v"],
                check=False,
                capture_output=True,
                text=True,
            )
            version = (raw.stdout or raw.stderr or "").strip()
            major = _node_major(version)
            report.node_ok = major is not None and major >= MIN_NODE_MAJOR
            if not report.node_ok:
                report.missing.append(f"Node {MIN_NODE_MAJOR}+（现在是 {version or '未知'}）")
        except OSError:
            report.missing.append(f"Node {MIN_NODE_MAJOR}+")
    else:
        report.missing.append(f"Node {MIN_NODE_MAJOR}+")

    report.npx = which("npx")
    if not report.npx:
        report.missing.append("npx")

    report.ffmpeg = which("ffmpeg")
    if not report.ffmpeg:
        report.missing.append("ffmpeg")

    if chrome_path is None:
        report.chrome = find_chrome(which=which)
    else:
        report.chrome = chrome_path or None
    if not report.chrome:
        report.missing.append("Chrome / Chromium（HyperFrames 渲染用）")

    report.ok = not report.missing
    if report.ok:
        report.notes.append(
            f"渲染宿主可用：Node 22+ / ffmpeg / Chrome。版本钉 hyperframes@{PINNED_HYPERFRAMES}。"
        )
    return report


def doctor_json(npx: str) -> dict:
    """Best-effort doctor payload. Version-pin 'failure' is ignored by callers."""

    env = os.environ.copy()
    env["HYPERFRAMES_NO_UPDATE_CHECK"] = "1"
    env["HYPERFRAMES_SKIP_SKILLS"] = "1"
    completed = subprocess.run(
        [npx, "--yes", f"hyperframes@{PINNED_HYPERFRAMES}", "doctor", "--json"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    text = completed.stdout or ""
    start = text.find("{")
    if start < 0:
        return {}
    try:
        payload = json.loads(text[start:])
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def chrome_from_doctor(payload: dict) -> str | None:
    for check in payload.get("checks") or []:
        if not isinstance(check, dict):
            continue
        if check.get("name") != "Chrome":
            continue
        if check.get("ok") is True:
            detail = str(check.get("detail") or "")
            path = detail.split(":", 1)[-1].strip() if ":" in detail else detail
            return path or "chrome"
    return None


def required_doctor_checks() -> Sequence[str]:
    return ("Node.js", "FFmpeg", "Chrome")
