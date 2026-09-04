# Design — top-ranking-demo

Canvas: **1080×1920 / 30fps**. HyperFrames pin: **0.6.69**.

## Palette

- Background: `#0a0a0d`
- Accent: `#7ad1c4` (single accent, dark field)
- Type: project-local WOFF2 only. Do not fetch Google Fonts at render time.

## Cover

- First-played song is rank **5** (last place), not rank 1.
- Dynamic footage from that clip, continuous into the first reveal.
- Title: `北城` is the unique largest type. Theme line is smaller.
- No song list, no `05→01`, no `N→1` mechanism text.
- If the title already says “被低估”, do not also stamp `TOP 5` on the cover.

## Type safety

Keep key copy inside `x=72–1008 / y=220–1420`. Do not dead-center over faces.
No custom narration captions unless a future brief explicitly asks.

## Motion

Cover is visible at t=0 (no fade-in from opacity 0). Rank cards fade as a
whole; do not stagger alpha on individual characters.
