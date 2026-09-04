#!/usr/bin/env python3
"""Central narration entry. Dry-run is the v1 default; Qwen/MLX is fail-closed.

Usage:
  python3 tools/tts/narrate.py --list-voices
  python3 tools/tts/narrate.py "text" --selection-file voice-selection.json -o out.wav --dry-run
  python3 tools/tts/narrate.py --batch narration-request.json --selection-file voice-selection.json --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from text_normalizer import normalize_tts_text
    from voice_registry import VoiceRegistry, resolve_selector
except ImportError:
    from tools.tts.text_normalizer import normalize_tts_text
    from tools.tts.voice_registry import VoiceRegistry, resolve_selector

TTS_ROOT = Path(__file__).resolve().parent


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_selection(path: Path | None, voice: str | None) -> dict:
    registry = VoiceRegistry.load()
    if path is not None:
        selection = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(selection, dict) or not selection.get("resolved_voice_id"):
            raise ValueError("selection file must contain resolved_voice_id")
        return selection
    if voice:
        return resolve_selector(registry, voice)
    raise ValueError("provide --selection-file or --voice")


def _sidecar(path: Path, selection: dict, source: str, normalized: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "resolved_voice_id": selection["resolved_voice_id"],
        "resolved_voice_name": selection.get("resolved_voice_name"),
        "engine": selection.get("engine"),
        "source_text": source,
        "text": normalized,
        "text_sha256": _sha256_text(source),
        "normalized_text_sha256": _sha256_text(normalized),
        "sample_rate_hz": 24000,
        "dry_run": True,
        "output": path.name,
    }


def _write_dry_run(output: Path, selection: dict, text: str) -> None:
    normalized = normalize_tts_text(text)
    output.parent.mkdir(parents=True, exist_ok=True)
    sidecar = output.with_name(output.name + ".tts.json")
    payload = _sidecar(output, selection, text, normalized.normalized_text)
    if normalized.changed:
        payload["normalized_text"] = normalized.normalized_text
        payload["pronunciation"] = normalized.metadata()
    sidecar.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Placeholder WAV is intentionally not written. Downstream gates treat
    # missing media as structure-only unless --require-media is set.


def _iter_batch(request_path: Path) -> list[dict]:
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    blocks = payload.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("batch request must contain a non-empty blocks array")
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", help="literal narration text")
    parser.add_argument("--batch", type=Path, help="JSON batch request")
    parser.add_argument("--selection-file", type=Path)
    parser.add_argument("--voice", help="exact ID/name/alias override")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="write sidecar JSON only (default when Qwen runtime is unset)",
    )
    args = parser.parse_args()

    if args.list_voices:
        registry = VoiceRegistry.load()
        for voice in registry.voices:
            print(f"{voice['id']}\t{voice['name']}\t{voice['slug']}")
        return 0

    try:
        selection = _load_selection(args.selection_file, args.voice)
    except ValueError as exc:
        print(f"NARRATE: FAIL — {exc}", file=sys.stderr)
        return 2

    dry_run = args.dry_run or True
    if args.batch:
        try:
            blocks = _iter_batch(args.batch)
            root = args.batch.parent
            for block in blocks:
                text = block["text"]
                output = root / block["output"]
                if "接下来" in text and block.get("id") == "intro":
                    print("NARRATE: FAIL — intro must not contain 接下来", file=sys.stderr)
                    return 1
                _write_dry_run(output, selection, text)
                print(output.with_name(output.name + ".tts.json"))
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            print(f"NARRATE: FAIL — {exc}", file=sys.stderr)
            return 1
        print("NARRATE: PASS dry-run batch")
        return 0

    if not args.text or not args.output:
        parser.error("single-shot narration requires TEXT and --output")
    if args.text.startswith("接下来"):
        print("NARRATE: FAIL — intro-style text must not start with 接下来", file=sys.stderr)
        return 1
    _write_dry_run(args.output, selection, args.text)
    print(args.output.with_name(args.output.name + ".tts.json"))
    print("NARRATE: PASS dry-run" if dry_run else "NARRATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
