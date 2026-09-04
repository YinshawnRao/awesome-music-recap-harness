#!/usr/bin/env bash
# 公开 YouTube 下载烟雾。只走 yt_dlp_readonly.py。
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
exec python3 "$ROOT/tools/video/smoke_download.py" "$@"
