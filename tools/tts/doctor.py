#!/usr/bin/env python3
"""TTS environment doctor. Checks registry, optional Metal, and user-added voices.

This scaffold ships registry stubs without proprietary reference WAVs. A
structure-only PASS means config/registry are valid. A voice-ready PASS
additionally finds the requested reference WAV plus the Qwen/MLX runtime.
Missing models fail closed. Never fall back to Kokoro.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
_REPO_ROOT = str(Path(_SCRIPT_DIR).parents[1])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from tools.tts.metal_preflight import default_metal_device_available
    from tools.tts.qwen_env import KOKORO_BAN, inspect_setup, resolve_qwen_model, resolve_qwen_python
    from tools.tts.voice_registry import VoiceRegistry
except ImportError:
    if _SCRIPT_DIR not in sys.path:
        sys.path.insert(0, _SCRIPT_DIR)
    from metal_preflight import default_metal_device_available
    from qwen_env import KOKORO_BAN, inspect_setup, resolve_qwen_model, resolve_qwen_python
    from voice_registry import VoiceRegistry


def run_doctor(voice_id: str | None = None, *, require_reference: bool = False) -> tuple[int, list[str]]:
    notes: list[str] = []
    registry = VoiceRegistry.load()
    notes.append(f"registry_voices={len(registry.voices)}")
    notes.append(f"preflight={registry.preflight_id}")
    notes.append(f"decision_pool={','.join(registry.decision_pool_ids)}")

    target_id = voice_id or registry.preflight_id
    voice = registry.by_id(target_id)
    if voice is None:
        return 1, [f"unknown voice {target_id}"]
    reference = registry.reference_path_for(voice)
    if reference.is_file():
        notes.append(f"reference=READY {reference.name}")
        voice_state = "READY"
    else:
        notes.append(f"reference=STUB missing {reference.as_posix()}")
        voice_state = "STUB"
        if require_reference:
            return 1, notes + [
                "reference WAV is required for this check",
                "缺参考：python3 tools/tts/install_reference.py ~/Desktop/reference.wav",
                KOKORO_BAN,
            ]

    if sys.platform == "darwin":
        metal = default_metal_device_available()
        notes.append("metal=PASS" if metal else "metal=FAIL")
        if not metal and require_reference:
            return 1, notes + ["Metal device unavailable for Qwen/MLX", KOKORO_BAN]
    else:
        notes.append("metal=SKIP (Linux/Kokoro is a documented future path)")

    qwen_python = resolve_qwen_python(registry)
    qwen_model = resolve_qwen_model(registry)
    notes.append("qwen_python=" + ("READY" if qwen_python else "UNSET"))
    notes.append("qwen_model=" + ("READY" if qwen_model else "UNSET"))

    generation_ready = voice_state == "READY" and bool(qwen_python) and bool(qwen_model)
    if require_reference:
        report = inspect_setup(target_id, check_mlx_import=False)
        if not report.ok or not generation_ready:
            extra = [f"- {error}" for error in report.errors]
            extra.append("真配音请跑：python3 tools/tts/setup_check.py")
            extra.append(KOKORO_BAN)
            notes.append(
                "TTS DOCTOR: FAIL "
                f"voice={target_id} state={voice_state}"
            )
            return 1, notes + extra

    notes.append(
        "TTS DOCTOR: "
        + ("PASS" if generation_ready else "PASS structure-only")
        + f" voice={target_id} state={voice_state}"
    )
    return 0, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", help="exact registered ID to inspect")
    parser.add_argument(
        "--require-reference",
        action="store_true",
        help="fail if the selected voice has no local reference WAV or Qwen runtime",
    )
    parser.add_argument(
        "--full-model-hash",
        action="store_true",
        help="reserved: full model-tree receipt is a local follow-up once weights exist",
    )
    args = parser.parse_args()
    if args.full_model_hash:
        print(
            "TTS DOCTOR: SKIP full-model-hash — model weights are not shipped; "
            "run this after you install a local Qwen Base tree",
            file=sys.stderr,
        )
    code, notes = run_doctor(args.voice, require_reference=args.require_reference)
    stream = sys.stdout if code == 0 else sys.stderr
    for note in notes:
        print(note, file=stream)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
