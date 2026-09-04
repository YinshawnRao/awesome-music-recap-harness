#!/usr/bin/env bash
# Vertical letterbox helper: any clip → 1080x1920, keep source aspect (fg
# scaled to 1080 wide, blurred background fill). Crop should be a FULL-WIDTH
# horizontal band (W:H:0:Y) to drop burned lyrics / watermarks. Do not pass a
# skinny vertical strip unless the user explicitly asked for a center-cut.
#
# Usage: vfill.sh <input> <output.mp4> <crop=W:H:X:Y> [brightness=-0.32] [sat=1.06]
set -euo pipefail
IN="$1"; OUT="$2"; CROP="$3"; BR="${4:--0.32}"; SAT="${5:-1.06}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BUDGET_RUNNER="$SCRIPT_DIR/resource_budget.py"
THREAD_TOKEN="__AMRH_THREADS__"

python3 "$BUDGET_RUNNER" ffmpeg -- ffmpeg -v error \
  -filter_threads "$THREAD_TOKEN" -filter_complex_threads "$THREAD_TOKEN" \
  -threads "$THREAD_TOKEN" -i "$IN" -filter_complex \
"[0:v]crop=${CROP},split=2[bg][fg];\
[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=${BR}:saturation=${SAT}[bgb];\
[fg]scale=1080:-2[fgs];\
[bgb][fgs]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]" \
-map "[v]" -map 0:a -c:v libx264 -threads "$THREAD_TOKEN" \
  -preset veryfast -r 30 -g 30 -keyint_min 30 -c:a aac -b:a 192k "$OUT" -y
echo "wrote $OUT ($(ffprobe -v error -show_entries stream=width,height -of csv=p=0:s=x "$OUT" | head -1))"
