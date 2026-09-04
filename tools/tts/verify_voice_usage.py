#!/usr/bin/env python3
"""VOICE GATE: selection, sidecar, and optional WAV consistency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from voice_registry import VoiceRegistry
except ImportError:
    from tools.tts.voice_registry import VoiceRegistry


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def verify_voice_usage(
    selection_path: Path,
    project_root: Path,
    *,
    require_wav: bool = False,
) -> tuple[list[str], str]:
    errors: list[str] = []
    registry = VoiceRegistry.load()
    try:
        selection = _load_json(selection_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"selection is unreadable: {exc}"]
    voice_id = selection.get("resolved_voice_id")
    if not isinstance(voice_id, str) or registry.by_id(voice_id) is None and not str(voice_id).startswith("kokoro:"):
        errors.append("resolved_voice_id is not a registered voice")
    if not registry.accepts_selection_hashes(selection):
        errors.append(
            "selection hashes do not match the current registry/config "
            "(regenerate voice-selection.json after a registry edit)"
        )

    sidecars = sorted(project_root.rglob("*.wav.tts.json"))
    if not sidecars:
        errors.append("no narration sidecars (*.wav.tts.json) found under project root")
        return errors

    seen_ids: set[str] = set()
    wav_count = 0
    readable = 0
    for sidecar_path in sidecars:
        try:
            sidecar = _load_json(sidecar_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{sidecar_path.name} is unreadable: {exc}")
            continue
        readable += 1
        resolved = sidecar.get("resolved_voice_id")
        if resolved != voice_id:
            errors.append(f"{sidecar_path.name} resolved_voice_id {resolved!r} != selection {voice_id!r}")
        if resolved:
            seen_ids.add(str(resolved))
        wav = sidecar_path.with_name(sidecar_path.name.removesuffix(".tts.json"))
        if wav.is_file():
            wav_count += 1
            continue
        if require_wav:
            errors.append(f"missing WAV for sidecar {sidecar_path.name}")
    if len(seen_ids) > 1:
        errors.append(f"multiple voice IDs in sidecars: {sorted(seen_ids)}")
    mode = "wav" if readable and wav_count == readable else "structure"
    return errors, mode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument(
        "--require-wav",
        action="store_true",
        help="fail if sidecar WAV files are missing (default: accept dry-run sidecars / structure mode)",
    )
    args = parser.parse_args()
    errors, mode = verify_voice_usage(args.selection, args.project_root, require_wav=args.require_wav)
    if errors:
        print("VOICE GATE: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"VOICE GATE: PASS mode={mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
