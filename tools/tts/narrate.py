#!/usr/bin/env python3
"""Central narration entry. Dry-run writes sidecars; real mode is fail-closed.

Usage:
  python3 tools/tts/narrate.py --list-voices
  python3 tools/tts/narrate.py "text" --selection-file voice-selection.json -o out.wav --dry-run
  python3 tools/tts/narrate.py --batch narration-request.json --selection-file voice-selection.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

_TTS_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = str(_TTS_ROOT.parents[1])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from tools.tts.qwen_env import KOKORO_BAN, SetupError, require_generation_ready
    from tools.tts.text_normalizer import normalize_tts_text
    from tools.tts.voice_registry import VoiceRegistry, resolve_selector
except ImportError:
    from qwen_env import KOKORO_BAN, SetupError, require_generation_ready
    from text_normalizer import normalize_tts_text
    from voice_registry import VoiceRegistry, resolve_selector

TTS_ROOT = _TTS_ROOT
WORKER = TTS_ROOT / "qwen_generate.py"


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


def _sidecar(path: Path, selection: dict, source: str, normalized: str, *, dry_run: bool) -> dict:
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
        "dry_run": dry_run,
        "output": path.name,
    }


def _write_sidecar(output: Path, selection: dict, text: str, *, dry_run: bool) -> Path:
    normalized = normalize_tts_text(text)
    output.parent.mkdir(parents=True, exist_ok=True)
    sidecar = output.with_name(output.name + ".tts.json")
    payload = _sidecar(output, selection, text, normalized.normalized_text, dry_run=dry_run)
    if normalized.changed:
        payload["normalized_text"] = normalized.normalized_text
        payload["pronunciation"] = normalized.metadata()
    sidecar.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return sidecar


def _write_dry_run(output: Path, selection: dict, text: str) -> None:
    _write_sidecar(output, selection, text, dry_run=True)
    # Placeholder WAV is intentionally not written. Downstream gates treat
    # missing media as structure-only unless --require-wav / --require-media.


def _reject_kokoro(selection: dict) -> None:
    engine = str(selection.get("engine") or "")
    voice_id = str(selection.get("resolved_voice_id") or "")
    if "kokoro" in engine.lower() or voice_id.startswith("kokoro:"):
        raise SetupError(f"NARRATE: FAIL — {KOKORO_BAN}")


def _write_real(output: Path, selection: dict, text: str) -> None:
    _reject_kokoro(selection)
    normalized = normalize_tts_text(text)
    runtime = require_generation_ready(selection["resolved_voice_id"])
    if not WORKER.is_file():
        raise SetupError("NARRATE: FAIL — 缺少 tools/tts/qwen_generate.py")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        runtime.qwen_python,
        str(WORKER),
        "--text",
        normalized.normalized_text,
        "--output",
        str(output),
        "--model",
        runtime.qwen_model,
        "--ref-audio",
        str(runtime.reference),
        "--ref-text",
        runtime.reference_text,
        "--language",
        runtime.language,
    ]
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0 or not output.is_file():
        raise SetupError(
            "NARRATE: FAIL — Qwen/MLX 没有写出 WAV。"
            f" 先跑 python3 tools/tts/setup_check.py。{KOKORO_BAN}"
        )
    _write_sidecar(output, selection, text, dry_run=False)


def _iter_batch(request_path: Path) -> list[dict]:
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    blocks = payload.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("batch request must contain a non-empty blocks array")
    return blocks


def _forbidden_intro(text: str, block_id: str | None = None) -> bool:
    if block_id == "intro" and "接下来" in text:
        return True
    return text.startswith("接下来")


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
        help="只写 sidecar JSON，不写音频（结构门禁用）",
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

    writer = _write_dry_run if args.dry_run else _write_real

    if args.batch:
        try:
            blocks = _iter_batch(args.batch)
            root = args.batch.parent
            for block in blocks:
                text = block["text"]
                output = root / block["output"]
                if _forbidden_intro(text, block.get("id")):
                    print("NARRATE: FAIL — intro must not contain 接下来", file=sys.stderr)
                    return 1
                writer(output, selection, text)
                print(output.with_name(output.name + ".tts.json"))
                if not args.dry_run:
                    print(output)
        except SetupError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            print(f"NARRATE: FAIL — {exc}", file=sys.stderr)
            return 1
        print("NARRATE: PASS dry-run batch" if args.dry_run else "NARRATE: PASS batch")
        return 0

    if not args.text or not args.output:
        parser.error("single-shot narration requires TEXT and --output")
    if _forbidden_intro(args.text):
        print("NARRATE: FAIL — intro-style text must not start with 接下来", file=sys.stderr)
        return 1
    try:
        writer(args.output, selection, args.text)
    except SetupError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(args.output.with_name(args.output.name + ".tts.json"))
    if not args.dry_run:
        print(args.output)
    print("NARRATE: PASS dry-run" if args.dry_run else "NARRATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
