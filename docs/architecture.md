# Architecture

AMRH is a **music recap / 盘点 harness**. A recap is any structured short-form
show built from sourced clips + narration + a composition layer. Ranking is
one shape, not the only shape.

## project_kind

```text
top_ranking  ── flagship demo (N→1 countdown, suspense)
narrative    ── timeline / essay / character documentary (script order, no rank)
free_exploration ── music or visual experiment (rationale required)
```

The authoring contract (`tools/video/project-manifest.schema.json`) is shared.
Gates branch on `project_kind` instead of hardcoding a single format into the
tools. `examples/top-ranking-demo/` is the reference implementation for rank.
A narrative project reuses the same voice, source, publishing, and mux rules
and simply omits `rank`.

## Layers

1. **Sourcing** — YouTube and Bilibili in parallel via `yt_dlp_readonly.py`,
   `bili_search.py`, and the documented `bili_dl.py` 412 fallback. Version
   identity first, official MV next, then cleanliness / stereo / resolution.
2. **Picture** — `vfill.sh` letterbox (full-width band). No aggressive
   vertical punch-in unless the user asked and every frame is checked.
3. **Voice** — parse once (`resolve_voice.py`), generate through `narrate.py`,
   verify with `verify_voice_usage.py`. Mac Qwen/MLX is the documented path.
4. **Plan** — `countdown_build.py` for TOP; narrative shows still fill schema
   v2 narration roles (intro, per-item transition, work outro, fixed CTA)
   unless they are a recorded free-exploration exception.
5. **Compose** — HyperFrames **0.6.69**, `--sdr`, workers via
   `resource_budget.py` (`4 → 3 → 2`).
6. **Mux** — premixed `master.wav` replaces HyperFrames audio.
7. **Publish** — `publishing/xiaohongshu.md` then FINAL skeleton.

## Resource budget

Heavy FFmpeg, ASR, and HyperFrames processes publish a PID marker under
`/tmp/amrh-resource-v1-<uid>/` and immediately pick 4, 3, or 2 workers. No
cross-job lock or queue. Override with `AMRH_FFMPEG_THREADS`,
`AMRH_HYPERFRAMES_WORKERS`, or `AMRH_ASR_THREADS` (1–4 only).

## Honesty boundary

Hashes, sidecars, and receipts prove **local consistency**. They are not a
proof of voice provenance, official-channel identity, or human review.
Never forge `reviewer_kind=human`.
