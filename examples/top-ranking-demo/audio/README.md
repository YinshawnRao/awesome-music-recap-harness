# 配音输出（不进 git）

`python3 tools/cli.py smoke-narrate` 的一句烟雾写在这里：

```text
examples/top-ranking-demo/audio/smoke.wav
```

整批教学旁白仍写到 `narration/*.wav`（和 `narration-request.json` / 清单对上），方便：

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo --require-wav
```

`*.wav` 已被 gitignore。不要提交真配音。缺权重时 `smoke-narrate` 会失败并打印中文下一步，不会改用 Kokoro。
