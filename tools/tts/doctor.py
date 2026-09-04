#!/usr/bin/env python3
"""TTS environment doctor. Checks registry, optional Metal, and user-added voices.

This scaffold ships registry stubs without proprietary reference WAVs. A
structure-only PASS means config/registry are valid. A voice-ready PASS
additionally finds the requested reference WAV. Qwen/MLX generation is
documented as the Mac-first path and is fail-closed when models are missing.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from metal_preflight import default_metal_device_available
    from voice_registry import VoiceRegistry
except ImportError:
    from tools.tts.metal_preflight import default_metal_device_available
    from tools.tts.voice_registry import VoiceRegistry

TTS_ROOT = Path(__file__).resolve().parent


def _qwen_python() -> str | None:
    env_name = VoiceRegistry.load().config["runtime"]["qwen_python_env"]
    configured = os.environ.get(env_name)
    if configured:
        return configured
    for candidate in VoiceRegistry.load().config["runtime"]["qwen_python_candidates"]:
        path = TTS_ROOT / candidate
        if path.is_file():
            return str(path)
    return None


def _qwen_model() -> str | None:
    registry = VoiceRegistry.load()
    for env_name in registry.config["runtime"]["qwen_base_model_envs"]:
        configured = os.environ.get(env_name)
        if configured:
            return configured
    for candidate in registry.config["runtime"]["qwen_base_model_candidates"]:
        path = TTS_ROOT / candidate
        if path.exists():
            return str(path)
    return None


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
            return 1, notes + ["reference WAV is required for this check"]

    if sys.platform == "darwin":
        metal = default_metal_device_available()
        notes.append("metal=PASS" if metal else "metal=FAIL")
        if not metal and require_reference:
            return 1, notes + ["Metal device unavailable for Qwen/MLX"]
    else:
        notes.append("metal=SKIP (Linux/Kokoro is a documented future path)")

    qwen_python = _qwen_python()
    qwen_model = _qwen_model()
    notes.append("qwen_python=" + ("READY" if qwen_python else "UNSET"))
    notes.append("qwen_model=" + ("READY" if qwen_model else "UNSET"))
    notes.append(
        "TTS DOCTOR: "
        + ("PASS" if voice_state == "READY" and qwen_python and qwen_model else "PASS structure-only")
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
