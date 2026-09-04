# tools/tts — narration doctor / resolve / narrate / verify

Operators start at the root [README](../../README.md). First success uses
the demo’s existing sidecars; you do not need to generate speech yet.

Public-facing Chinese narration helpers. The Mac-first generation path is
**Qwen3-TTS Base via MLX**. Model weights and proprietary reference WAVs are
**not shipped**.

## Commands

```bash
python3 tools/tts/doctor.py
python3 tools/tts/resolve_voice.py --task-prompt-file brief.txt \
  --model-choice CV007 \
  --model-reason 'Theme is archival and documentary.' \
  --model-confidence high \
  -o voice-selection.json
python3 tools/tts/narrate.py --batch narration-request.json \
  --selection-file voice-selection.json --dry-run
python3 tools/tts/verify_voice_usage.py \
  --selection voice-selection.json --project-root .
```

`--dry-run` writes `.wav.tts.json` sidecars without audio. That is enough for
the VOICE gate in structure-only mode. Real generation needs:

1. Apple Silicon + Metal (see `metal_preflight.py`)
2. `AMRH_QWEN_PYTHON` pointing at an MLX-Audio 0.4.5 interpreter
3. `AMRH_QWEN_BASE_MODEL` pointing at a legally obtained Qwen3-TTS Base tree
4. A reference WAV for the resolved `CVxxx` (see `voices/README.md`)

Missing models fail closed. Do **not** silently fall back to Kokoro.

## Voice selection

Parse once per project. Exact `配音：CV007` wins. Otherwise the contributor
picks from the 10-voice decision pool using theme / emotion / narrative angle /
pacing, and passes `--model-choice` plus a short reason. `low` confidence
randomizes inside the same pool.

Do not pick voice gender from artist gender.

## Legal / open alternatives

- Record your own reference clips.
- Use openly licensed speech you have permission to condition on.
- Kokoro-82M is documented as a Linux/future explicit-legacy engine only.

HyperFrames built-in TTS is not used for Chinese.
