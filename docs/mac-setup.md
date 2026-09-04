# Mac setup

v1 is **Mac-first**. These are the expected local tools.

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

## Cookies (optional)

Export a Netscape jar from your browser, filter it outside the repo, then
install it yourself as `all_cookies.txt` with mode `0600`.

```bash
python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
  --output /absolute/outside/candidate.txt
# You copy candidate → repo-root all_cookies.txt and chmod 600
python3 tools/video/check_yt_cookie.py
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

The wrapper never lets yt-dlp rewrite the canonical jar.

## Linux / Kokoro

Mentioned only as a future explicit-legacy engine (`hexgrad/Kokoro-82M`).
Not required to use this harness in v1.

## Tests without media

```bash
python3 -m pytest
```
