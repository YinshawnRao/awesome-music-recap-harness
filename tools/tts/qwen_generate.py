#!/usr/bin/env python3
"""Qwen3-TTS / MLX worker. Must run under AMRH_QWEN_PYTHON.

Metal is checked before importing MLX. Missing weights or Metal → fail.
Never fall back to Kokoro. Weights are never downloaded here (offline).
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

TTS_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = str(TTS_ROOT.parents[1])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from tools.tts.metal_preflight import MetalUnavailable, require_default_metal_device
    from tools.tts.qwen_env import KOKORO_BAN, SetupError
except ImportError:
    if str(TTS_ROOT) not in sys.path:
        sys.path.insert(0, str(TTS_ROOT))
    from metal_preflight import MetalUnavailable, require_default_metal_device
    from qwen_env import KOKORO_BAN, SetupError


def preflight_metal() -> None:
    """Fail before any MLX import if this process cannot use Metal."""
    try:
        require_default_metal_device()
    except MetalUnavailable as error:
        raise SetupError(
            "没有 Metal，不能加载 MLX。"
            f" 请在 Apple Silicon Mac 本机终端重跑。{KOKORO_BAN}"
            f" 原文：{error}"
        ) from error


def generate_wav(
    *,
    text: str,
    output: Path,
    model: Path,
    ref_audio: Path,
    ref_text: str,
    language: str = "Auto",
) -> Path:
    preflight_metal()
    try:
        from mlx_audio.tts.generate import generate_audio
        from mlx_audio.tts.utils import load_model
    except ImportError as error:
        raise SetupError(
            "当前解释器没有 mlx-audio 0.4.5。"
            " 请确认 AMRH_QWEN_PYTHON 指向 tools/tts/qwen.venv/bin/python，"
            f"并先跑 bash tools/tts/bootstrap_mac.sh。{KOKORO_BAN}"
        ) from error

    if not model.is_dir():
        raise SetupError(f"模型目录不存在：{model}。权重不随仓库分发。")
    if not ref_audio.is_file():
        raise SetupError(f"参考 WAV 不存在：{ref_audio}")

    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="amrh-tts-"))
    try:
        loaded = load_model(model_path=str(model))
        generate_audio(
            model=loaded,
            text=text,
            ref_audio=str(ref_audio),
            ref_text=ref_text,
            output_path=str(tmp),
            file_prefix="chunk",
            audio_format="wav",
            join_audio=True,
            play=False,
            stream=False,
            verbose=True,
            lang_code=language,
        )
        produced = sorted(path for path in tmp.glob("*.wav") if path.is_file())
        if not produced:
            raise SetupError(
                "Qwen/MLX 跑完但没有写出 WAV。"
                " 请看上面的 mlx-audio 原文。常见原因：参考句和录音对不上、模型树不完整。"
                f" {KOKORO_BAN}"
            )
        preferred = tmp / "chunk.wav"
        source = preferred if preferred.is_file() else produced[0]
        shutil.copyfile(source, output)
    except SetupError:
        raise
    except Exception as error:
        raise SetupError(
            "Qwen/MLX 生成失败（不是改用 Kokoro 的理由）。"
            f" 核对 AMRH_QWEN_BASE_MODEL 和参考 WAV 后重跑。原文：{error}"
        ) from error
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if not output.is_file() or output.stat().st_size < 64:
        raise SetupError(f"输出 WAV 无效：{output}")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--ref-audio", required=True, type=Path)
    parser.add_argument("--ref-text", required=True)
    parser.add_argument("--language", default="Auto")
    args = parser.parse_args(argv)
    try:
        dest = generate_wav(
            text=args.text,
            output=args.output,
            model=args.model,
            ref_audio=args.ref_audio,
            ref_text=args.ref_text,
            language=args.language,
        )
    except SetupError as error:
        print(f"QWEN GENERATE: FAIL — {error}", file=sys.stderr)
        return 1
    print(dest)
    print("QWEN GENERATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
