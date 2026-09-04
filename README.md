# awesome-music-recap-harness

A **music 盘点 harness** for making a vertical ranking short: pick songs,
source clips from YouTube + Bilibili, narrate, package, publish.

This repo is a **guide you can follow**, not a dump of internals. Read this
page and [`examples/top-ranking-demo/`](examples/top-ranking-demo/). License:
**MIT**. v1 is **Mac-first**.

## Who this is for

You want to produce a ranking recap (TOP / 榜单, playback **N→1**) and you
have a Mac with Homebrew. You do not need to learn every tool on day one.

## What you get

- A flagship teaching project: fictional artist **北城**, five labeled
  placeholder songs (not a real copyrighted setlist)
- A cookie-safe download path (required for a real render)
- Four gates so you know when the structure is sound
- A known “done” file: `renders/<slug>.mp4` plus Xiaohongshu copy

Media, model weights, voice masters, and **real cookies are not shipped**.

## 1. Mac prerequisites (copy-paste)

```bash
brew install ffmpeg yt-dlp
# Node 22+ (Homebrew node, fnm, or nvm)
node -v          # expect v22 or newer
python3 --version
ffmpeg -version | head -n 1
yt-dlp --version

npx --yes hyperframes@0.6.69 doctor
python3 tools/tts/doctor.py
```

Always pin HyperFrames to **0.6.69**. Do not use `@latest`.

## 2. Cookies (required for the full flow)

Downloads will not start without repo-root `all_cookies.txt` (mode `0600`).
The structure walkthrough in §3 still runs without a real login.

```bash
cp examples/cookies/all_cookies.example.txt all_cookies.txt
chmod 0600 all_cookies.txt
```

That example is **fake** (`PLACEHOLDER_NOT_A_SESSION_*`). It is not a login.

**Export a real Netscape jar** from your browser (signed into YouTube/Google
**and** Bilibili). Use a `cookies.txt` exporter such as “Get cookies.txt
LOCALLY”. Save the dump **outside this repo**, then overwrite the runtime
file yourself:

```bash
# raw dump and candidate must live outside the repository
python3 tools/video/filter_cookie_jar.py "$HOME/Downloads/raw-cookies.txt" \
  --output "$HOME/Downloads/candidate-cookies.txt"
cp "$HOME/Downloads/candidate-cookies.txt" all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

`check_yt_cookie.py` never prints cookie values. It **fails** while
placeholder tokens remain — that is expected until you install a real
export. Never commit `all_cookies.txt`. The only allowed yt-dlp consumer is
`tools/video/yt_dlp_readonly.py` (it copies the jar outside the repo so
yt-dlp cannot rewrite it).

More detail: [examples/cookies/README.md](examples/cookies/README.md).

## 3. First success — run the TOP demo

From the repository root. The demo already has a brief, voice selection,
manifest, narration sidecars, and publishing copy. You are checking that
the **structure** walks:

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo

python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo
```

Expected lines:

```text
VOICE GATE: PASS
PROJECT CONTRACT: PASS mode=structure
PUBLISHING COPY: PASS
FINAL VIDEO QA: PASS skeleton pending_machine_qa
```

Folder map, brief, and the later download/render steps live in
[examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md).

## 4. What “done” looks like

| Stage | You have | Gates |
| --- | --- | --- |
| **First success (today)** | Structure + countdown plan, no bundled video | VOICE, PROJECT, PUBLISHING, FINAL skeleton all **PASS** |
| **A finished ranking short** | `examples/top-ranking-demo/renders/top-ranking-demo.mp4` and `publishing/xiaohongshu.md` | Same four gates; publishing after mux |

A real mp4 needs **your** licensed source URLs (replace the `example.com`
placeholders in `SOURCES.md`), a **real** cookie jar, narration WAVs, and a
HyperFrames composition. Full media download depends on your cookies and
network. The demo does not ship clips.

When you are ready to render (after sources exist):

```bash
# download only through the readonly wrapper
python3 tools/video/yt_dlp_readonly.py -- "<YOUR_URL>" -o "examples/top-ranking-demo/downloads/%(id)s.%(ext)s"
# letterbox, narrate (not --dry-run), HyperFrames 0.6.69 --sdr, then:
ffmpeg -i examples/top-ranking-demo/renders/full.mp4 \
  -i examples/top-ranking-demo/master.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  examples/top-ranking-demo/renders/top-ranking-demo.mp4
```

Exact per-folder commands: the [demo README](examples/top-ranking-demo/README.md).

## 5. Troubleshooting (top 5)

**Cookie check fails.** Missing `all_cookies.txt`, mode not `0600`, leftover
`PLACEHOLDER_*` values, or a dump that lacks YouTube/Google + Bilibili
names. Copy the example, export a real Netscape file, `chmod 0600`, rerun
`python3 tools/video/check_yt_cookie.py`. Never run `yt-dlp --cookies`
yourself.

**`ffmpeg` not found.** `brew install ffmpeg` and open a new terminal.
`which ffmpeg` should print a Homebrew path.

**`node -v` below 22.** HyperFrames 0.6.69 needs Node 22+. Upgrade with
Homebrew / fnm / nvm, then `hash -r` and check `node -v` again.

**HyperFrames pin.** Only `npx --yes hyperframes@0.6.69 ...`. Bare
`npx hyperframes` or `@latest` is wrong. From the demo folder,
`npm run lint` / `npm run render` already pin 0.6.69.

**TTS doctor unhappy.** Structure gates do not need a generated WAV.
`--dry-run` / existing `.wav.tts.json` sidecars are enough for first
success. Real speech needs Apple Silicon, a legal Qwen/MLX install, and
your own `reference.wav` — see [docs/mac-setup.md](docs/mac-setup.md).
Do not silently switch to Kokoro.

## After first success

Do not start here.

| Want | Read |
| --- | --- |
| Teaching project (brief → folders → render) | [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md) |
| Cookie export details | [examples/cookies/README.md](examples/cookies/README.md) |
| Mac TTS / extra install notes | [docs/mac-setup.md](docs/mac-setup.md) |
| Your own ranking short after the demo | [docs/runbook.md](docs/runbook.md) |
| Why the pipeline is shaped this way | [docs/architecture.md](docs/architecture.md) |
| Other show shapes, Baidu upload, hard media gates | [docs/beyond-the-demo.md](docs/beyond-the-demo.md) |
| Production conventions | [CONVENTIONS.md](CONVENTIONS.md) |
| Secondary doc index | [docs/README.md](docs/README.md) |
