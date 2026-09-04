# Voice registry stubs

This directory ships **IDs, names, aliases, and decision profiles only**.

It does **not** ship proprietary reference WAVs, cloned celebrity voices, or model weights.

## Add a voice

1. Keep the permanent `CVxxx` ID. Never reuse an ID for a different voice.
2. Record or license a short reference WAV that matches `registry.json` `reference_text` (or a per-voice `reference_text`).
3. Place it at the `reference_audio` path, for example `CV001-calm-narrator/reference.wav`.
4. Run `python3 tools/tts/doctor.py --voice CV001`.
5. Generate samples only from voices you have the right to use.

Legal alternatives for the Mac path:

- Train or record your own reference clips.
- Use openly licensed speech you have permission to condition on.
- On Linux, a future Kokoro path is documented but not required for v1.

Do not commit cookies, tokens, or large WAVs unless you intend them as public fixtures and they are clearly licensed.
