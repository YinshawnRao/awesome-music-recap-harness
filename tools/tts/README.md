# tools/tts — 旁白体检 / 选声 / 配音 / 校验

请从根目录 [README](../../README.md) 开始。本地 AI Agent 请同时遵守 [AGENTS.md](../../AGENTS.md)。第一次跑通用教学示例已有的 sidecar；现在还不必生成语音。

面向中文口播的辅助工具。Mac 上的生成路径是 **Qwen3-TTS Base + MLX**。模型权重和专有参考 WAV **不随仓库分发**。缺了就失败，并打印中文下一步。**不要改用 Kokoro。**

## 命令

```bash
python3 tools/tts/doctor.py
python3 tools/tts/setup_check.py
python3 tools/tts/install_reference.py ~/Desktop/reference.wav
python3 tools/cli.py smoke-narrate
python3 tools/tts/resolve_voice.py --task-prompt-file brief.txt \
  --model-choice CV007 \
  --model-reason 'Theme is archival and documentary.' \
  --model-confidence high \
  -o voice-selection.json
python3 tools/tts/narrate.py --batch narration-request.json \
  --selection-file voice-selection.json --dry-run
python3 tools/tts/verify_voice_usage.py \
  --selection voice-selection.json --project-root .
```

`--dry-run` 只写 `.wav.tts.json` sidecar，不写音频。结构模式下的 VOICE 门禁够用（`VOICE GATE: PASS mode=structure`）。

真生成**不要**加 `--dry-run`。需要：

1. Apple Silicon + Metal（见 `metal_preflight.py`）
2. `AMRH_QWEN_PYTHON` 指向 MLX-Audio 0.4.5 解释器（`bash tools/tts/bootstrap_mac.sh`）
3. `AMRH_QWEN_BASE_MODEL` 指向合法取得的 Qwen3-TTS Base 模型树
4. 已解析 `CVxxx` 对应的参考 WAV（见 [voices/local/README.md](voices/local/README.md)）

模型缺失就失败退出。**不要**悄悄回退到 Kokoro。

Mac 复制步骤：[docs/mac-setup.md](../../docs/mac-setup.md)。

## VOICE 门禁两种模式

| 模式 | 条件 | 命令 |
| --- | --- | --- |
| 结构 | 只有 sidecar | `verify_voice_usage.py` → `PASS mode=structure` |
| 真 WAV | 每个 sidecar 旁边都有 `.wav` | 加 `--require-wav` → `PASS mode=wav` |

教学示例的单句试生成写在 `examples/top-ranking-demo/audio/`（gitignore）。整批写在 `narration/*.wav`。

## 选声

每个项目只解析一次。简报里的精确写法 `配音：CV007` 优先。否则贡献者按主题 / 情绪 / 叙事角度 / 节奏，从 10 个声音决策池里选，并传入 `--model-choice` 和一句短理由。`low` 置信度会在同一池内随机。

不要按艺人性别选配音性别。

## 合法 / 开放替代

- 录自己的参考片段（开箱默认）。
- 用你有权作为条件的开放授权语音。
- Kokoro-82M 只作为 Linux / 将来的显式旧引擎写在文档里。

中文口播不用 HyperFrames 内置 TTS。
