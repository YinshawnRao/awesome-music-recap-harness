# Beyond the demo

Read this after the root README and the TOP-ranking example. Nothing here
is required for first success.

## Other show shapes

The authoring contract (`project_kind`) also accepts:

| Kind | Meaning |
| --- | --- |
| `top_ranking` | Flagship. N→1 countdown, suspense on cover/intro. |
| `narrative` | Timeline / essay order. Items have no `rank`. |
| `free_exploration` | Experiment; needs a non-empty `rationale`. |

Use the same voice, source, publishing, and mux rules. Do not start a new
shape until you have walked the ranking demo once.

## Hard media gates

Structure mode is the default so the demo runs without bundled clips.

```bash
python3 tools/video/verify_project.py --project examples/top-ranking-demo --require-media
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo --require-wav
```

Those flags fail until real WAVs / clips exist.

## Optional Baidu upload

`tools/delivery/baidu/` is an **optional** plugin. The harness does not
depend on it. Tokens never belong in git. See
[tools/delivery/baidu/README.md](../tools/delivery/baidu/README.md).

## Command appendix

Full command lists (vfill, bili search, resource budget, cookie filter)
live in [tools/video/README.md](../tools/video/README.md) and
[tools/tts/README.md](../tools/tts/README.md). Prefer the demo walkthrough
until you need one of those tools.
