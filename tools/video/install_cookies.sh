#!/usr/bin/env bash
# 把格式模板拷到仓库根目录 all_cookies.txt（0600），并打印下一步导出说明。
# 不打印 Cookie 值，也不改写已有的真实 jar。
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/install_cookies.py" "$@"
