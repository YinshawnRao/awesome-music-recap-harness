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
masters, real session cookies, or private shows. A format-only Netscape
example lives at `examples/cookies/all_cookies.example.txt`.

## Quickstart (Mac)

```bash
brew install ffmpeg yt-dlp
# Node >= 22 for HyperFrames

# Required for the full dual-platform download pipeline (not for structure gates)
cp examples/cookies/all_cookies.example.txt all_cookies.txt
chmod 0600 all_cookies.txt
# Replace PLACEHOLDER_* values with a real Netscape export (see docs/mac-setup.md)
python3 tools/video/check_yt_cookie.py

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

More: [docs/mac-setup.md](docs/mac-setup.md), [docs/runbook.md](docs/runbook.md),
[docs/architecture.md](docs/architecture.md).

Linux / Kokoro is a **future** path, not required for v1.

## Architecture in one page

```text
all_cookies.txt (0600) ── yt_dlp_readonly.py snapshot ── YouTube + Bilibili clips
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

## Cookie rule (required for the full pipeline)

The dual-platform yt-dlp flow **requires** a Netscape cookie jar. Structure
gates (`VOICE` / `PROJECT` / `PUBLISHING` / FINAL skeleton) still run without
one. Downloads do not.

1. Export a Netscape cookie file from your browser (YouTube/Google + Bilibili
   session). See [docs/mac-setup.md](docs/mac-setup.md) and
   [examples/cookies/README.md](examples/cookies/README.md).
2. Filter **outside the repo** with `tools/video/filter_cookie_jar.py`.
3. Install the candidate yourself:

   ```bash
   cp examples/cookies/all_cookies.example.txt all_cookies.txt   # format template
   # or: cp /absolute/outside/candidate.txt all_cookies.txt
   chmod 0600 all_cookies.txt
   python3 tools/video/check_yt_cookie.py
   ```

4. Consume the jar **only** through `tools/video/yt_dlp_readonly.py`. That
   wrapper copies the file to a private temp directory **outside the
   repository** so yt-dlp cannot rewrite `all_cookies.txt`.

**Never commit `all_cookies.txt`.** The gitignored runtime file is yours. The
committed `all_cookies.example.txt` is fake (`PLACEHOLDER_NOT_A_SESSION_*`)
and is not a login. `check_yt_cookie.py` fails the example on purpose until
placeholder values are replaced.

## What is not in this repo

- Personal artist lists or private production shows
- Real session cookies, Baidu tokens, or sandbox renders
- Proprietary voice master WAVs (registry stubs + add-your-own docs instead)
- Model weights

## Tests

```bash
python3 -m pytest
```

## HyperFrames pin

New compositions use **`hyperframes@0.6.69` only**. No bare `npx hyperframes`
and no `@latest`.
