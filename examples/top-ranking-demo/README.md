# Flagship demo: TOP ranking countdown

Teaching project for a **vertical ranking short**. Follow this folder after
the root [README](../../README.md).

Artist **北城** and the five titles below are **fictional placeholders**.
They are not a required copyrighted setlist. Replace URLs before any real
download.

## 1. Brief — what you are making

Read [`BRIEF.md`](BRIEF.md) first. In one line:

> 北城 · 被低估的5首现场 · 竖屏 1080×1920 · playback **N→1** (5→1) ·
> cover/intro do not list the setlist or leak #1 · voice CV007

| Rank (playback order) | Title | Performer | Label |
| --- | --- | --- | --- |
| 5 (plays first) | 纸灯笼 | 北城 | placeholder |
| 4 | 夜渡 | 北城 | placeholder |
| 3 | 玻璃港 | 北城 | placeholder |
| 2 | 北窗 | 北城 | placeholder |
| 1 (plays last) | 末班月台 | 北城 | placeholder |

Sources: [`SOURCES.md`](SOURCES.md) (`example.com` only until you lock real
URLs). Design notes: [`design.md`](design.md).

## 2. Folders you should see

```text
examples/top-ranking-demo/
  BRIEF.md                 why this show exists
  SOURCES.md               dual-platform URL table (placeholders)
  songs.json               N→1 playback list
  project-manifest.json    schema v2 contract
  voice-selection.json     one voice for the whole show
  narration-request.json   TTS batch
  narration/*.wav.tts.json sidecars (enough for structure VOICE)
  publishing/xiaohongshu.md
  qa/                      FINAL skeleton lands here
  package.json             hyperframes@0.6.69 pin
  downloads/               you create — raw yt-dlp output (gitignored)
  clips/                   you create — letterboxed verticals (gitignored)
  renders/                 you create — full.mp4 then <slug>.mp4 (gitignored)
```

Nothing under `downloads/`, `clips/`, or `renders/` is bundled. First
success does not need those folders.

## 3. Commands (from the repository root)

### First success — structure only

No cookies, no clips, no TTS models:

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo

python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo
```

Re-resolve the voice or re-dry-run narration only if you change the brief
(see [docs/runbook.md](../../docs/runbook.md)). Do not start there.

### After you have real URLs + a real cookie jar

1. Replace every `example.com` row in `SOURCES.md` with sources you may use.
2. Confirm `python3 tools/video/check_yt_cookie.py` prints
   `static preflight: PASS` (not the placeholder example).
3. Download **only** through the wrapper:

   ```bash
   python3 tools/video/yt_dlp_readonly.py -- "<YOUR_URL>" \
     -o "examples/top-ranking-demo/downloads/%(id)s.%(ext)s"
   ```

4. Letterbox each clip (`vfill.sh` full-width band) into `clips/vert_rank-0N.mp4`.
5. Generate narration WAVs (drop `--dry-run` once TTS doctor is green).
6. From this folder, pin-render then mux:

   ```bash
   npm run render
   ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a \
     -c:v copy -c:a aac -b:a 192k -shortest renders/top-ranking-demo.mp4
   ```

`npm run render` is `npx --yes hyperframes@0.6.69 render --output renders/full.mp4 --sdr`.

## 4. Gates — what PASS looks like

| Gate | Command | Success line |
| --- | --- | --- |
| VOICE | `verify_voice_usage.py` | `VOICE GATE: PASS` |
| PROJECT | `verify_project.py` | `PROJECT CONTRACT: PASS mode=structure` |
| PUBLISHING | `verify_publishing.py` | `PUBLISHING COPY: PASS` |
| FINAL | `prepare_final_qa.py` | `FINAL VIDEO QA: PASS skeleton pending_machine_qa` |

v1 FINAL writes a pending skeleton. It does not prove the picture or ASR.

## 5. Done

- **Today:** the four lines above. You understand the ranking short.
- **Finished file:** `renders/top-ranking-demo.mp4` + `publishing/xiaohongshu.md`.
  That second stage needs your cookies, network, and licensed media.
