# CONVENTIONS.md — portable production standards

Humans start at [README.md](README.md). This file is the red-line list,
not the first-success guide. Tool READMEs hold extra commands. `AGENTS.md`
holds contributor automation. Do not fork conflicting rules.

## Git boundary

Commit source, docs, schemas, briefs, light QA JSON, and the **fake**
Netscape template `examples/cookies/all_cookies.example.txt`. Do not commit
downloads, renders, ordinary WAV/MP4, the runtime cookie jar, tokens, or
model weights. Root `all_cookies.txt` is a user-only input (`0600`), not a
git asset. `.gitignore` ignores `*cookies*.txt` and un-ignores the example.

## Recap shapes

盘点 is broader than a TOP list. Set `project_kind` explicitly:

- `top_ranking` — countdown, N→1 playback, cover/intro keep suspense.
- `narrative` — timeline or essay order; items have no `rank`.
- `free_exploration` — experiment; non-empty `rationale`.

New projects use authoring **schema v2**.

## Dual-platform sources

Search YouTube **and** Bilibili unless the brief names one URL as mandatory.
Lock version identity first (cover vs original performer), then official MV,
then cleanliness, stereo, and resolution. Record the choice in `SOURCES.md`
and `project-manifest.json`. Placeholder example.com URLs are for the demo
only.

## TOP ranking (flagship)

- Playback N→1. That order is internal (scripts, timeline, QA).
- Cover and intro do not list the full setlist, show the order, or leak #1.
- Do not paint `05→01` / `N→1` / “倒数开始” on screen.
- If the cover title already uses a Chinese superlative (“最难 / 最燃 /
  被低估”), do not also stamp an extra `TOP N` badge on the cover.
- Cover footage is the **first-played** song (last place), flowing into that
  reveal.

## Narration

- Structure: intro + per-item short transition + work outro + fixed CTA.
- Intro must not contain “接下来”.
- TOP transitions: one reveal + one judgment; target 4–6s, hard cap 8s WAV.
- Narrative transitions: node + one meaning; target 6–8s, hard cap 10s WAV.
- Fixed CTA is `tools/video/outro_cta.py::FIXED_OUTRO_CTA` and is the last
  spoken line. Briefs do not replace it.
- One `voice-selection.json` per project. Do not pick voice gender from
  artist gender.
- Qwen missing → fail the TTS step. Do not silently use Kokoro.
- Pure Chinese is not rewritten. ASCII tokens may be normalized
  (`BEYOND → Beyond`, `BTS → B T S`).

## Picture

- Default canvas 1080×1920 @ 30fps.
- Letterbox via `vfill.sh` with a **full-width** crop band.
- No custom narration captions unless the brief asks.
- No watermarks, URLs, prompts, or file paths on the finished frame.
- Fonts: project-local licensed WOFF2. No Google Fonts at render time.

## Audio

- Duck music under narration (~25%, 300ms).
- Premix `master.wav`, then mux after HyperFrames (HF flattens dynamics).
- `>1.5s` silence is a hard fail on a real final. Do not bed noise to pass.

## HyperFrames

Pin **0.6.69**. Render with `--sdr`. Start workers through
`tools/video/resource_budget.py` (`4 → 3 → 2`, overrides `AMRH_*` 1–4).

## Publishing

`publishing/xiaohongshu.md` after mux, before FINAL. 1–5 title candidates
(default 3), 420–900 non-space body characters, a real question, 8–10
hashtags, no emoji, no song titles.

## Optional Baidu

`tools/delivery/baidu/` is upload-only and reads `AMRH_BAIDU_*` or a secret
file. No tokens in git.
