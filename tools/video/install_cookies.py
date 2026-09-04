#!/usr/bin/env python3
"""Copy the format-only Cookie example to repo-root all_cookies.txt.

Does not print Cookie values. Never overwrites a non-placeholder jar.
Prints the next browser-export steps in Simplified Chinese.
"""

from __future__ import annotations

import argparse
import shutil
import stat
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_REL = Path("examples") / "cookies" / "all_cookies.example.txt"
RUNTIME_NAME = "all_cookies.txt"

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from check_yt_cookie import inspect_jar
except ImportError:  # python -m / package import
    from tools.video.check_yt_cookie import inspect_jar


class InstallCookiesError(RuntimeError):
    """User-actionable Cookie install failure (no secrets)."""


def example_jar(repo_root: Path) -> Path:
    return repo_root / EXAMPLE_REL


def runtime_jar(repo_root: Path) -> Path:
    return repo_root / RUNTIME_NAME


def jar_state(path: Path) -> str:
    """Return missing | placeholder | ready. Values are never returned."""
    if not path.is_file():
        return "missing"
    try:
        inspection = inspect_jar(path)
    except OSError as error:
        raise InstallCookiesError(f"无法读取 Cookie 文件：{path.name}") from error
    if inspection.placeholder_values:
        return "placeholder"
    return "ready"


def install_example_jar(
    repo_root: Path | str | None = None,
    dest: Path | str | None = None,
    *,
    force: bool = False,
) -> tuple[Path, str]:
    """Copy the example jar if needed. Returns (dest, action).

    action is one of: copied | already-placeholder | already-ready | replaced-placeholder
    """
    root = REPO_ROOT if repo_root is None else Path(repo_root)
    source = example_jar(root)
    target = runtime_jar(root) if dest is None else Path(dest)
    if not source.is_file():
        raise InstallCookiesError(f"缺少格式模板：{EXAMPLE_REL.as_posix()}")

    existed = target.is_file()
    state = jar_state(target) if existed else "missing"
    if existed and state == "ready" and not force:
        return target, "already-ready"
    if existed and state == "placeholder" and not force:
        mode = stat.S_IMODE(target.stat().st_mode)
        if mode & 0o077:
            target.chmod(0o600)
        return target, "already-placeholder"

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    target.chmod(0o600)
    if existed and state == "placeholder":
        return target, "replaced-placeholder"
    return target, "copied"


def _print_next_steps(state: str, dest: Path) -> None:
    print(f"文件：{dest.name}（不打印内容）")
    if state == "copied":
        print("已拷贝格式模板，权限 0600。里面全是假的 PLACEHOLDER_*，不能登录。")
    elif state == "already-placeholder":
        print("已有占位 jar（0600）。没有覆盖。")
    elif state == "replaced-placeholder":
        print("已用格式模板覆盖占位 jar，权限 0600。")
    elif state == "already-ready":
        print("已有非占位 jar，没有覆盖。完整下载请再跑：")
        print("  python3 tools/video/check_yt_cookie.py")
        return

    print()
    print("下一步（密钥不要进仓库）：")
    print("  1. 同一浏览器配置里登录 YouTube/Google 和 B 站")
    print("  2. 用 cookies.txt 插件导出 Netscape 文件，先存到仓库外，chmod 0600")
    print("  3. 筛选后再覆盖运行时文件：")
    print(
        "     python3 tools/video/filter_cookie_jar.py "
        '"$HOME/Downloads/raw-cookies.txt" \\'
    )
    print('       --output "$HOME/Downloads/candidate-cookies.txt"')
    print(f'     cp "$HOME/Downloads/candidate-cookies.txt" {RUNTIME_NAME}')
    print(f"     chmod 0600 {RUNTIME_NAME}")
    print("     python3 tools/video/check_yt_cookie.py")
    print()
    print("公开 YouTube 样本在部分网络可以不登录就下；")
    print("B 站和完整教学下载仍必须换成真实导出。")
    print("下载只走：python3 tools/video/yt_dlp_readonly.py -- <URL>")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="把格式模板拷到仓库根目录 all_cookies.txt（0600），并打印导出步骤。",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="仓库根目录（默认：本文件上两级）",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="目标路径（默认：<repo-root>/all_cookies.txt）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已有非占位 jar（一般不要用）",
    )
    args = parser.parse_args(argv)
    try:
        dest, action = install_example_jar(
            repo_root=args.repo_root,
            dest=args.dest,
            force=args.force,
        )
    except InstallCookiesError as error:
        print(f"COOKIE 安装: FAIL — {error}")
        return 2
    _print_next_steps(action, dest)
    print("COOKIE 安装: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
