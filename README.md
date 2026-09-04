# awesome-music-recap-harness

Open-source **music recap / 盘点 harness** for other people to run, fork, and
teach from. It is a pipeline, not a clip dump: dual-platform sourcing,
narration, HyperFrames packaging, four quality gates, and an optional upload
plugin.

**TOP ranking countdown is the flagship demo.** The architecture is not limited
to rank lists. `project_kind` also supports narrative / timeline essays and
free-exploration experiments.

License: **MIT** (see `LICENSE`).

## Why this exists

A stranger should be able to:

1. Install FFmpeg, yt-dlp, Node 22, and Python 3 on a Mac.
2. Fill a project contract (`project-manifest.json` schema v2).
3. Resolve one voice, generate narration sidecars, plan an N→1 countdown.
4. Pass VOICE → PROJECT → PUBLISHING → FINAL gates.
5. Optionally upload a finished file to Baidu Netdisk **without** committing tokens.

This repository ships **structure and tools**, not model weights, voice
masters, cookies, or private shows.

## Quickstart (Mac)

```bash
brew install ffmpeg yt-dlp
# Node >= 22 for HyperFrames
python3 tools/tts/doctor.py
python3 tools/tts/resolve_voice.py --list

# Flagship demo (no media bundled)
python3 tools/tts/resolve_voice.py \
  --task-prompt-file examples/top-ranking-demo/BRIEF.md \
  --model-choice CV007 \
  --model-reason 'Archival documentary tone for an underrated-live ranking.' \
  --model-confidence high \
  -o examples/top-ranking-demo/voice-selection.json

python3 tools/tts/narrate.py --batch examples/top-ranking-demo/narration-request.json \
  --selection-file examples/top-ranking-demo/voice-selection.json --dry-run

python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo

python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo
```

More: [docs/mac-setup.md](docs/mac-setup.md), [docs/architecture.md](docs/architecture.md).

Linux / Kokoro is a **future** path, not required for v1.

## Architecture in one page

```text
YouTube + Bilibili ── yt-dlp readonly wrapper ── clips
                              │
                              ▼
                     vfill.sh letterbox 1080×1920
                              │
TTS (Qwen/MLX on Mac) ── voice-selection.json ── narration WAVs + sidecars
                              │
                              ▼
              VOICE gate → PROJECT contract → countdown plan
                              │
              HyperFrames 0.6.69 render --sdr (resource_budget workers)
                              │
                     mux master.wav over picture
                              │
              PUBLISHING (xiaohongshu.md) → FINAL QA skeleton
                              │
                     optional Baidu upload plugin
```

`project_kind`:

| Kind | Meaning | Flagship? |
| --- | --- | --- |
| `top_ranking` | N→1 countdown, suspense on cover/intro | **Yes — see `examples/top-ranking-demo/`** |
| `narrative` | Timeline / essay order, no `rank` | Supported by the same contract |
| `free_exploration` | Music/visual experiment; needs `rationale` | Supported; not the demo |

## Gates

1. **VOICE** — one resolved voice for the whole show; sidecars match.
2. **PROJECT** — schema v2, dual-platform search, TOP rules, canonical CTA.
3. **PUBLISHING** — `publishing/xiaohongshu.md` structure, no song-title spoilers.
4. **FINAL** — v1 writes a pending `qa/final-video-qa.json` skeleton.

Structure mode is the default so the demo runs without bundled media.
`--require-media` / `--require-wav` are the production switches.

## Cookie rule

Provide your own Netscape jar as repo-root `all_cookies.txt` (`0600`) if a
site requires login. **Never commit cookies.** All yt-dlp calls go through
`tools/video/yt_dlp_readonly.py`, which copies the jar outside the repo so
yt-dlp cannot rewrite the canonical file.

## What is not in this repo

- Personal artist lists or private production shows
- Real cookies, Baidu tokens, or sandbox renders
- Proprietary voice master WAVs (registry stubs + add-your-own docs instead)
- Model weights

## Tests

```bash
python3 -m pytest
```

## HyperFrames pin

New compositions use **`hyperframes@0.6.69` only**. No bare `npx hyperframes`
and no `@latest`.
