# Operator runbook

From a filled brief to a structured recap. The flagship shape is a **TOP
ranking countdown (N→1)**. The same contract also supports `narrative` and
`free_exploration` via `project_kind`.

Companion command list: [tools/video/README.md](../tools/video/README.md).
Mac install: [mac-setup.md](mac-setup.md).

## 0. Cookie jar (required before any real download)

The dual-platform yt-dlp flow **will not start** without repo-root
`all_cookies.txt` (mode `0600`). Structure gates do not need it.

1. Export a Netscape jar from the browser (YouTube/Google + Bilibili).
2. Keep the raw dump **outside** the repository; `chmod 0600`.
3. Filter outside the repo:

   ```bash
   python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
     --output /absolute/outside/candidate.txt
   ```

4. Install the candidate yourself (tools never write this path):

   ```bash
   cp /absolute/outside/candidate.txt all_cookies.txt
   chmod 0600 all_cookies.txt
   python3 tools/video/check_yt_cookie.py
   ```

5. Download **only** through the readonly wrapper:

   ```bash
   python3 tools/video/yt_dlp_readonly.py -- "<URL>" --skip-download --print id,title
   ```

The wrapper snapshots the jar to a private temp directory **outside the
repository** (`amrh-cookie-*`) so yt-dlp cannot rewrite `all_cookies.txt`.
Do not call `yt-dlp --cookies` yourself. Do not commit the runtime file.
The committed `examples/cookies/all_cookies.example.txt` is fake format
only; `check_yt_cookie.py` fails it until placeholder values are replaced.

## 1. Voice

```bash
python3 tools/tts/doctor.py
python3 tools/tts/resolve_voice.py --task-prompt-file <BRIEF.md> \
  --model-choice CV007 --model-reason '...' --model-confidence high \
  -o <project>/voice-selection.json
python3 tools/tts/narrate.py --batch <project>/narration-request.json \
  --selection-file <project>/voice-selection.json --dry-run
python3 tools/tts/verify_voice_usage.py \
  --selection <project>/voice-selection.json --project-root <project>
```

## 2. Project contract (before master / HTML)

Fill `project-manifest.json` (schema v2), search YouTube **and** Bilibili,
then:

```bash
python3 tools/video/verify_project.py --project <project>
python3 tools/video/countdown_build.py --project <project> --plan-only
```

## 3. Picture + mux

Letterbox with `tools/video/vfill.sh` (full-width band). Render HyperFrames
**0.6.69** `--sdr` through `resource_budget.py`. Mux premixed `master.wav`
after render (HF flattens dynamics).

## 4. Publishing + FINAL

```bash
python3 tools/video/verify_publishing.py --project <project>
python3 tools/video/prepare_final_qa.py --project <project>
```

v1 FINAL writes a pending skeleton. Do not claim a finished machine
picture/ASR audit, and do not forge `reviewer_kind=human`.
