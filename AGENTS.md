# AGENTS.md

Humans start at [README.md](README.md) and
[examples/top-ranking-demo/](examples/top-ranking-demo/). This file is for
contributor automation, not the operator guide. Keep operator-specific
goal quirks out of this file.

## Intent

Help another person follow the README and finish the TOP-ranking demo.
Do not lead with every `project_kind` or optional plugin.

The teaching project is `examples/top-ranking-demo/` (N→1). Other shapes
are documented in `docs/beyond-the-demo.md` after first success.

## Layout

- `tools/tts/` — doctor, resolve, narrate, verify
- `tools/video/` — cookies, yt-dlp wrapper, vfill, gates, countdown planner
- `examples/top-ranking-demo/` — teaching TOP project
- `examples/cookies/` — Netscape format template (fake values only)
- `docs/` — secondary material after first success
- `tools/delivery/baidu/` — optional; not part of first success

## Start of a video task

1. Read `README.md` and `examples/top-ranking-demo/README.md`. Then
   `CONVENTIONS.md` if you need a red-line.
2. Run `python3 tools/tts/doctor.py` (structure-only PASS is OK until voices exist).
3. Resolve **one** `voice-selection.json` from the original brief. Only
   re-run this if the brief changed; the demo already has a selection.
4. A Netscape jar at repo-root `all_cookies.txt` (`0600`) is **required**
   before any real download. Copy `examples/cookies/all_cookies.example.txt`,
   replace placeholder values with a filtered browser export, then
   `python3 tools/video/check_yt_cookie.py`. The only allowed yt-dlp
   consumer is `yt_dlp_readonly.py` (temp snapshot outside the repo). Never
   rewrite `all_cookies.txt`. Missing or placeholder cookies → stop the
   download step; structure-only gates may continue.
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

Never commit the runtime jar (`all_cookies.txt`), Baidu tokens, `.env`, or
voice masters you do not intend to publish. The committed cookie example is
fake format only. The Baidu module is optional.

## HyperFrames

`npx --yes hyperframes@0.6.69 ...` only. Render `--sdr`. Fonts offline.
