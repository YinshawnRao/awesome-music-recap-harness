# Your own ranking short

Use this after you have run the [TOP demo](../examples/top-ranking-demo/)
and the root README first-success commands. Copy that folder’s shape, not
every script in `tools/`.

## 1. Copy the teaching layout

```text
BRIEF.md
SOURCES.md
songs.json                 # playback N→1
project-manifest.json      # schema v2
voice-selection.json
narration-request.json
publishing/xiaohongshu.md
package.json               # hyperframes@0.6.69
```

Keep cover/intro free of the full setlist and of `#1`.

## 2. Cookies, then sources

A real Netscape jar at repo-root `all_cookies.txt` (`0600`) is required
before download. `python3 tools/video/check_yt_cookie.py` must PASS.

Search YouTube **and** Bilibili. Lock version identity first, then official
MV, then cleanliness. Write the choice in `SOURCES.md` and the manifest.
Download only through `tools/video/yt_dlp_readonly.py`.

## 3. Voice, then project gate

One voice for the whole show. Dry-run narration is enough until TTS doctor
is green. `verify_project.py` must print `PROJECT CONTRACT: PASS` **before**
you write `master.wav` or composition HTML.

```bash
python3 tools/video/countdown_build.py --project <project> --plan-only
```

## 4. Picture, render, mux

Letterbox with `tools/video/vfill.sh` (full-width band). Render
**hyperframes@0.6.69** `--sdr`. Mux premixed `master.wav` over the picture
(HyperFrames flattens dynamics):

```bash
ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest renders/<slug>.mp4
```

## 5. Publishing + FINAL

```bash
python3 tools/video/verify_publishing.py --project <project>
python3 tools/video/prepare_final_qa.py --project <project>
```

v1 FINAL writes a pending skeleton. Do not claim a finished machine
picture/ASR audit, and do not forge `reviewer_kind=human`.

Other shapes, Baidu, and `--require-media`: [beyond-the-demo.md](beyond-the-demo.md).
