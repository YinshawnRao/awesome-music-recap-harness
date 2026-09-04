# tools/video — sourcing, gates, countdown

Runbook from brief to a structured recap. The flagship shape is a **TOP ranking
countdown (N→1)**. The same contract also supports `narrative` (timeline /
essay) and `free_exploration` via `project_kind`.

## Commands

```bash
# Cookie-safe download (user-provided jar only; never commit cookies)
python3 tools/video/yt_dlp_readonly.py -- "<URL>" --skip-download --print id,title

# Dual-platform search
python3 tools/video/bili_search.py "PLACEHOLDER artist official MV" 5

# Letterbox to 1080×1920 (full-width crop band)
bash tools/video/vfill.sh raw.mp4 clips/vert_item.mp4 1920:800:0:140

# Gates
python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo

# Flagship planner
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only

# Adaptive HyperFrames workers (from the project directory)
python3 ../../tools/video/resource_budget.py hyperframes -- \
  npx --yes hyperframes@0.6.69 render --output renders/full.mp4 --sdr
```

## Four gates (order is fixed)

1. **VOICE** — `tools/tts/verify_voice_usage.py`
2. **PROJECT** — `verify_project.py` (before writing master.wav / HTML)
3. **PUBLISHING** — `verify_publishing.py` after mux, before FINAL
4. **FINAL** — `prepare_final_qa.py` (v1 writes a pending skeleton)

`--require-media` / `--require-wav` turn structure PASS into a media-hard gate.

## master.wav mux

HyperFrames normalizes audio and flattens ducking. Always mux a premixed
`master.wav` over the video:

```bash
ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest renders/<slug>.mp4
```

## Cookies

`all_cookies.txt` at the repo root is user-maintained, mode `0600`, never
committed. Agents and scripts must not rewrite it. Use `yt_dlp_readonly.py`.
If the jar is missing, continue with public downloads and the other platform.
