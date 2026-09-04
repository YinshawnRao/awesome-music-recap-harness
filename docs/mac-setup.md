# Mac setup (appendix)

The short copy-paste path is the root [README](../README.md). This page
adds TTS detail and a fuller cookie table. v1 is **Mac-first**.

## Required

```bash
brew install ffmpeg yt-dlp
# Node 22+ (Homebrew node, fnm, or nvm)
node -v   # >= 22
python3 --version
```

HyperFrames:

```bash
npx --yes hyperframes@0.6.69 doctor
```

Always pass the pin `0.6.69`. Do not use `@latest`.

## Cookies (required for the full download pipeline)

A Netscape cookie jar is **required** to run the dual-platform YouTube +
Bilibili yt-dlp flow. Structure-only demo gates still pass without one.
Do not treat cookies as an optional nicety.

The committed file `examples/cookies/all_cookies.example.txt` is **format
only**: valid Netscape header and columns, fake `PLACEHOLDER_NOT_A_SESSION_*`
values. It cannot log anyone in. Root `all_cookies.txt` is gitignored.

### Export from a browser

Use an extension that writes a **Netscape HTTP Cookie File** (tab-separated
`cookies.txt`). Typical names: “Get cookies.txt LOCALLY”, “cookies.txt”.
Export while you are signed into YouTube/Google **and** Bilibili. Save the
raw dump **outside this repository** (for example `~/Downloads/raw-cookies.txt`)
and `chmod 0600` it immediately.

You need both field families:

| Platform | Required names | Typical domains |
| --- | --- | --- |
| YouTube / Google | `LOGIN_INFO`, `SID`, `HSID`, `SSID`, `SAPISID`, `APISID`, `__Secure-3PSID` | `.youtube.com`, `.google.com` |
| Bilibili | `SESSDATA`, `bili_jct`, `DedeUserID` | `.bilibili.com` |

Do **not** pass `--cookies-from-browser` through this harness. The only
allowed yt-dlp consumer of the canonical jar is the readonly wrapper.

### Install path

```bash
# 1) Start from the committed format template (optional but recommended)
cp examples/cookies/all_cookies.example.txt all_cookies.txt

# 2) Filter a real browser dump outside the repo (source and output must be outside)
python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
  --output /absolute/outside/candidate.txt

# 3) You copy the candidate over the runtime file. Tools never write this path.
cp /absolute/outside/candidate.txt all_cookies.txt
chmod 0600 all_cookies.txt

# 4) Static preflight (does not print values; fails on leftover PLACEHOLDER_*)
python3 tools/video/check_yt_cookie.py

# 5) Only allowed yt-dlp consumer — snapshots the jar outside the repo
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

`yt_dlp_readonly.py` copies `all_cookies.txt` to a private `amrh-cookie-*`
directory under the system temp folder so yt-dlp cannot rewrite the
canonical file on exit. Never invoke `yt-dlp --cookies all_cookies.txt`
directly.

## Optional Qwen / MLX TTS

On Apple Silicon:

1. Create a dedicated interpreter (do not mix it with a generic Whisper venv).
2. Install a legal copy of `mlx-audio==0.4.5` and the Qwen3-TTS 0.6B Base
   8-bit tree documented in `tools/tts/config.json`.
3. Export:

```bash
export AMRH_QWEN_PYTHON=/path/to/qwen.venv/bin/python
export AMRH_QWEN_BASE_MODEL=/path/to/Qwen3-TTS-12Hz-0.6B-Base-8bit@REVISION
```

4. Add your own licensed `reference.wav` under `tools/tts/voices/CVxxx-*/`.
5. `python3 tools/tts/doctor.py --voice CV007 --require-reference`

`metal_preflight.py` checks Metal **before** importing MLX. If Metal is
missing, the current TTS step fails closed. Do not silently switch to Kokoro.

## Linux / Kokoro

Mentioned only as a future explicit-legacy engine (`hexgrad/Kokoro-82M`).
Not required to use this harness in v1.

## Tests without media

```bash
python3 -m pytest
```
