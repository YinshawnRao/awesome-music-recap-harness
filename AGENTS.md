# AGENTS.md

Contributor / automation runbook for this public harness. Keep operator-specific
goal quirks out of this file.

## Intent

Help another person build a music recap with:

1. Dual-platform sourcing (YouTube + Bilibili)
2. One project-level voice
3. A `project_kind` that may be rank, narrative, or free-exploration
4. HyperFrames 0.6.69 packaging and `master.wav` mux
5. VOICE → PROJECT → PUBLISHING → FINAL gates

The flagship example is `examples/top-ranking-demo/` (N→1). Do not assume every
brief is a ranking show.

## Layout

- `tools/tts/` — doctor, resolve, narrate, verify
- `tools/video/` — cookies, yt-dlp wrapper, vfill, gates, countdown planner
- `tools/delivery/baidu/` — optional upload
- `examples/top-ranking-demo/` — placeholder TOP scaffold
- `docs/` — architecture and Mac setup

## Start of a video task

1. Read `CONVENTIONS.md` and `tools/video/README.md`.
2. Run `python3 tools/tts/doctor.py` (structure-only PASS is OK until voices exist).
3. Resolve **one** `voice-selection.json` from the original brief.
4. Use `yt_dlp_readonly.py` for any cookie-backed yt-dlp. Never rewrite
   `all_cookies.txt`. Missing cookies → continue with public + other platform.
5. Fill `project-manifest.json` (schema v2) **before** writing master/HTML.
6. `verify_project.py` must print `PROJECT CONTRACT: PASS`.
7. After mux, write `publishing/xiaohongshu.md` and run `verify_publishing.py`.
8. Run `prepare_final_qa.py`. v1 writes a pending skeleton; do not claim a
   finished machine picture/ASR audit, and do not forge human review.

## Recovery

A failed step stops that step, not the whole task. Diagnose → fix upstream →
rerun affected gates. Do not relax mechanical red lines. Do not invent
`reviewer_kind=human`.

Pause only when the user asked for a preview, a required user-only file is
missing, safe alternatives are exhausted, or continuing would change the
core brief (setlist, ranks, version, platform exclusion, hard duration).

## Resources

Use `tools/video/resource_budget.py`. No global lock across jobs. Env overrides
are `AMRH_ASR_THREADS`, `AMRH_FFMPEG_THREADS`, `AMRH_HYPERFRAMES_WORKERS` (1–4).

## Secrets

Never commit cookies, Baidu tokens, `.env`, or voice masters you do not intend
to publish. The Baidu module is optional.

## HyperFrames

`npx --yes hyperframes@0.6.69 ...` only. Render `--sdr`. Fonts offline.
