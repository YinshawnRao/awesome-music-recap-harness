#!/usr/bin/env bash
# Apple Silicon + Qwen3-TTS / MLX 安装助手。
# 不下载模型权重（仓库不随附）。缺条件就失败，绝不改用 Kokoro。
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
VENV="$SCRIPT_DIR/qwen.venv"
RUNTIME_DIR="$SCRIPT_DIR/runtime"
ENV_SH="$RUNTIME_DIR/env.sh"
PINNED_MLX_AUDIO="0.4.5"
MODEL_ID="mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit"
MODEL_REVISION="50f45ef0047cde7e84c2ef04326acb8ada2436a7"
DEFAULT_MODEL_DIR="${HOME}/amrh-models/Qwen3-TTS-12Hz-0.6B-Base-8bit"

fail() {
  echo "TTS BOOTSTRAP: FAIL — $*" >&2
  echo "不要改用 Kokoro。v1 真配音只走 Apple Silicon 上的 Qwen3-TTS + MLX。" >&2
  exit 2
}

uname_s="$(uname -s)"
uname_m="$(uname -m)"
if [[ "$uname_s" != "Darwin" ]]; then
  fail "当前是 ${uname_s}/${uname_m}，不是 macOS。请换 M 系列 Mac，见 docs/mac-setup.md。"
fi
if [[ "$uname_m" != "arm64" && "$uname_m" != "aarch64" ]]; then
  fail "当前是 ${uname_s}/${uname_m}。需要 Apple Silicon（M 系列），Intel Mac 没有这条 MLX 路径。"
fi

if ! command -v python3 >/dev/null 2>&1; then
  fail "找不到 python3。先装 Xcode Command Line Tools 或 brew install python。"
fi

python_ver="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
python_major="$(python3 -c 'import sys; print(sys.version_info[0])')"
python_minor="$(python3 -c 'import sys; print(sys.version_info[1])')"
if (( python_major < 3 || python_minor < 10 )); then
  fail "python3 是 ${python_ver}，mlx-audio ${PINNED_MLX_AUDIO} 需要 3.10+。"
fi

echo "系统: Darwin ${uname_m}（Apple Silicon）"
echo "python3: $(command -v python3)  (${python_ver})"

if ! python3 "$SCRIPT_DIR/metal_preflight.py"; then
  fail "Metal 预检没过。在本机终端重跑，不要用无 GPU 的远程会话。"
fi

echo "建立虚拟环境（与 Whisper / 系统包分开）：$VENV"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install "mlx-audio==${PINNED_MLX_AUDIO}"

if ! "$VENV/bin/python" -c "import importlib.metadata as m; v=m.version('mlx-audio'); assert v.startswith('${PINNED_MLX_AUDIO}'), v"; then
  fail "mlx-audio ${PINNED_MLX_AUDIO} 安装后验包失败。"
fi

mkdir -p "$RUNTIME_DIR"
cat > "$ENV_SH" <<EOF
# AMRH Qwen/MLX 环境（本文件 gitignore，不要提交）
export AMRH_QWEN_PYTHON="${VENV}/bin/python"
# 权重不随仓库分发。下载完成后把下一行改成你的本地目录：
export AMRH_QWEN_BASE_MODEL="\${AMRH_QWEN_BASE_MODEL:-${DEFAULT_MODEL_DIR}}"
EOF

echo
echo "已写入（gitignore）：${ENV_SH#"$REPO_ROOT"/}"
echo
echo "权重不随仓库分发（约 2GB）。请你自己从模型卡合法下载："
echo "  模型：https://huggingface.co/${MODEL_ID}"
echo "  钉 revision：${MODEL_REVISION}"
echo
echo "  python3 -m pip install -U huggingface_hub"
echo "  huggingface-cli download ${MODEL_ID} \\"
echo "    --revision ${MODEL_REVISION} \\"
echo "    --local-dir \"${DEFAULT_MODEL_DIR}\""
echo
echo "然后在每个新终端："
echo "  source ${ENV_SH#"$REPO_ROOT"/}"
echo "  python3 tools/tts/setup_check.py"
echo
echo "参考 WAV（教学项目默认 CV007）："
echo "  见 tools/tts/voices/local/README.md"
echo "  python3 tools/tts/install_reference.py ~/Desktop/reference.wav"
echo
echo "TTS BOOTSTRAP: OK — 解释器已就绪，权重还要你自己下载。"
