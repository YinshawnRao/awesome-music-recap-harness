# tools/video — command appendix

Operators start at the root [README](../../README.md) and
[examples/top-ranking-demo/](../../examples/top-ranking-demo/). This page
lists extra commands. You do not need most of them for first success.

## Commands

```bash
# Cookie-safe download (REQUIRED jar; only allowed yt-dlp consumer)
python3 tools/video/check_yt_cookie.py
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

## Cookies (required for the full pipeline)

The dual-platform download flow **requires** a Netscape jar at repo-root
`all_cookies.txt` (mode `0600`). Structure-only gates still run without it.
Missing or placeholder jars are a hard stop for `yt_dlp_readonly.py` and
`check_yt_cookie.py`.

1. Copy the committed format template, or overwrite it with a filtered export:

   ```bash
   cp examples/cookies/all_cookies.example.txt all_cookies.txt
   chmod 0600 all_cookies.txt
   ```

2. Export a real Netscape file from the browser (YouTube/Google + Bilibili).
   Filter **outside the repo** (`filter_cookie_jar.py` refuses in-repo paths).
   You copy the candidate onto `all_cookies.txt`. Tools never write that path.

3. Verify:

   ```bash
   python3 tools/video/check_yt_cookie.py
   ```

   The check never prints cookie values. The example file fails on purpose
   while `PLACEHOLDER_*` tokens remain.

4. Download **only** via `yt_dlp_readonly.py`. It copies the jar to a private
   `amrh-cookie-*` directory outside the repository so yt-dlp cannot rewrite
   the canonical file. Do not run `yt-dlp --cookies all_cookies.txt`.

See [examples/cookies/README.md](../../examples/cookies/README.md). Other
show shapes and Baidu: [docs/beyond-the-demo.md](../../docs/beyond-the-demo.md).
