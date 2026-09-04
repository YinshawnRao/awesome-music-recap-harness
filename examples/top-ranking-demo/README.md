# Flagship demo: TOP ranking countdown

Generic placeholder recap for **北城** (fictional artist). Songs are labeled
sample placeholders, not a required copyrighted setlist.

## What this folder proves

- `project_kind: top_ranking`
- Playback order **N→1** (5 → 1) in `songs.json` and `project-manifest.json`
- Cover / intro do not list the setlist or print `N→1`
- Four-gate file layout: voice selection, authoring contract, Xiaohongshu copy, QA skeleton
- HyperFrames pin `0.6.69` in `package.json`

Media files are **not** bundled. Structure gates pass without them.

## Run the scaffold

From the repository root:

```bash
python3 tools/tts/resolve_voice.py --task-prompt-file examples/top-ranking-demo/BRIEF.md \
  --model-choice CV007 \
  --model-reason 'Archival, documentary tone for an underrated-live ranking.' \
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

Replace placeholder URLs in `SOURCES.md` with sources you have the right to use
before any real download or render.
