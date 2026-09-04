#!/usr/bin/env python3
"""P1 public YouTube download smoke — yt_dlp_readonly.py only.

Downloads Jawed Karim's *Me at the zoo* (jNQXAC9IVRw), the first YouTube
upload (2005-04-23). It is a short, well-known public sample — not a music
MV — used here only to prove the Cookie + yt-dlp wrapper path.

The wrapper always needs repo-root all_cookies.txt. Some networks can fetch
this public video without a real login; Bilibili and the full demo path
still require a real Netscape export.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WRAPPER = Path(__file__).resolve().parent / "yt_dlp_readonly.py"
SMOKE_VIDEO_ID = "jNQXAC9IVRw"
SMOKE_URL = f"https://www.youtube.com/watch?v={SMOKE_VIDEO_ID}"
DEFAULT_OUT_REL = Path("examples") / "smoke-download" / "out"

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from check_yt_cookie import default_cookie_path, inspect_jar
except ImportError:  # python -m / package import
    from tools.video.check_yt_cookie import default_cookie_path, inspect_jar


class SmokeDownloadError(RuntimeError):
    """User-actionable smoke failure (no secrets)."""


def cookie_state(path: Path) -> str:
    """Return missing | placeholder | ready. Values are never returned."""
    if not path.is_file():
        return "missing"
    try:
        inspection = inspect_jar(path)
    except OSError as error:
        raise SmokeDownloadError(f"无法读取 Cookie 文件：{path.name}") from error
    if inspection.placeholder_values:
        return "placeholder"
    return "ready"


def _print_missing_cookie_fix() -> None:
    print("COOKIE 预检: 缺失 — 没有仓库根目录 all_cookies.txt", flush=True)
    print()
    print("本仓库只允许 python3 tools/video/yt_dlp_readonly.py 调 yt-dlp，")
    print("封装必须读这份 jar（拷到仓库外的临时快照，不会改原文件）。")
    print("部分网络可以不登录就下公开 YouTube；B 站 / 完整教学下载仍要真实导出。")
    print()
    print("下一步：")
    print("  bash tools/video/install_cookies.sh")
    print("  # 然后用浏览器 Netscape 导出覆盖占位值，再：")
    print("  python3 tools/video/check_yt_cookie.py")


def _print_placeholder_warning() -> None:
    print("COOKIE 预检: 占位符 — 还是 PLACEHOLDER_*，不能当登录态", flush=True)
    print("公开 YouTube 样本在部分网络可以不登录就下；本命令仍走 yt_dlp_readonly.py。")
    print("B 站和完整教学下载必须换成真实导出。见 examples/cookies/README.md")


def preflight(
    repo_root: Path,
    *,
    allow_placeholder: bool = True,
) -> str:
    """Check Cookie jar. Raises SmokeDownloadError on a hard stop."""
    jar = default_cookie_path(repo_root)
    state = cookie_state(jar)
    if state == "missing":
        _print_missing_cookie_fix()
        raise SmokeDownloadError("缺少 all_cookies.txt")
    if state == "placeholder":
        _print_placeholder_warning()
        if not allow_placeholder:
            print()
            print("下一步：用真实 Netscape 导出覆盖 all_cookies.txt 后重跑。")
            raise SmokeDownloadError("Cookie 仍是占位符")
        return state
    print("COOKIE 预检: 非占位 jar（值未打印）")
    return state


def _require_tools() -> None:
    if shutil.which("yt-dlp") is None:
        raise SmokeDownloadError(
            "找不到 yt-dlp。Mac：brew install yt-dlp。装好后重开终端。"
        )
    if not WRAPPER.is_file():
        raise SmokeDownloadError("缺少 tools/video/yt_dlp_readonly.py")


def run_smoke_download(
    repo_root: Path,
    out_dir: Path,
    *,
    url: str = SMOKE_URL,
    extra_yt_dlp: list[str] | None = None,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    template = str(out_dir / "%(id)s.%(ext)s")
    command = [
        sys.executable,
        str(WRAPPER),
        "--",
        url,
        "--no-playlist",
        "--no-overwrites",
        "-o",
        template,
        *(extra_yt_dlp or []),
    ]
    print("下载入口: tools/video/yt_dlp_readonly.py", flush=True)
    print(f"样本: {url}", flush=True)
    print(f"输出: {out_dir}", flush=True)
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


def _found_outputs(out_dir: Path, video_id: str) -> list[Path]:
    if not out_dir.is_dir():
        return []
    matches = sorted(
        path
        for path in out_dir.iterdir()
        if path.is_file() and path.name.startswith(video_id) and path.suffix != ".part"
    )
    return matches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="公开 YouTube 下载烟雾（只走 yt_dlp_readonly.py）。",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="仓库根目录（默认：本文件上两级）",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="输出目录（默认：examples/smoke-download/out）",
    )
    parser.add_argument(
        "--strict-cookies",
        action="store_true",
        help="占位 jar 直接失败，不尝试公开样本",
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    out_dir = (
        args.out_dir.resolve()
        if args.out_dir is not None
        else (repo_root / DEFAULT_OUT_REL)
    )

    print("为什么是 Me at the zoo（jNQXAC9IVRw）：", flush=True)
    print("  YouTube 上第一条公开上传（2005-04-23，Jawed Karim），约 19 秒，")
    print("  不是音乐 MV，常被用来测 yt-dlp。本烟雾只为证明下载封装能跑。")
    print(flush=True)

    try:
        state = preflight(repo_root, allow_placeholder=not args.strict_cookies)
        _require_tools()
    except SmokeDownloadError as error:
        print(f"SMOKE DOWNLOAD: FAIL — {error}")
        return 2

    code = run_smoke_download(repo_root, out_dir)
    outputs = _found_outputs(out_dir, SMOKE_VIDEO_ID)
    if code == 0 and outputs:
        print()
        print("SMOKE DOWNLOAD: PASS")
        for path in outputs:
            print(f"  {path}")
        if state == "placeholder":
            print()
            print("注意：这次用的是占位 Cookie。公开样本成功 ≠ B 站能下。")
            print("完整教学路径请换成真实导出后再跑 check_yt_cookie.py。")
        return 0

    print()
    print("SMOKE DOWNLOAD: FAIL")
    print("公开样本没下来。常见原因：网络 / 地区限制 / Cookie 仍是假的。")
    print("若 yt-dlp 写 Sign in to confirm you’re not a bot，就是占位 Cookie 不够。")
    print("可执行修复：")
    print("  bash tools/video/install_cookies.sh")
    print("  # 用真实 Netscape 导出覆盖 all_cookies.txt")
    print("  python3 tools/video/check_yt_cookie.py")
    print("  python3 tools/cli.py smoke-download")
    print("部分网络不登录也能下这条公开视频；本命令仍然只走 yt_dlp_readonly.py。")
    print("B 站和完整 demo 必须有真实 Cookie。不要自己跑 yt-dlp --cookies。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
