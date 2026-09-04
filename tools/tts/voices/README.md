# 声音登记（仅元数据）

本目录只提供 **ID、名称、别名和决策画像**。

**不**提供专有参考 WAV、明星克隆声，或模型权重。

本机自录的参考装在 **[local/](local/README.md)**（gitignore），教学示例默认 **CV007**。

## 加一个声音

1. 保留永久 `CVxxx` ID。不要把同一个 ID 复用到另一个声音。
2. 录制或取得有授权的短参考 WAV，文本对齐 `registry.json` 的 `reference_text`（或该声音自己的 `reference_text`）。
3. 用安装器放进本地声槽（不要提交真实 WAV）：

   ```bash
   python3 tools/tts/install_reference.py ~/Desktop/reference.wav --voice CV001
   ```

   实际路径：`tools/tts/voices/local/CV001/reference.wav`。登记里的 `CV001-calm-narrator/reference.wav` 仍可作为后备。
4. 跑 `python3 tools/tts/setup_check.py --voice CV001`。
5. 只从你有权使用的声音生成样例。

Mac 路径的合法替代：

- 自己训练或录参考片段。
- 用你有权作为条件的开放授权语音。
- Linux 上将来的 Kokoro 路径有文档，但 v1 不需要。

不要提交 Cookie、token，或大体积 WAV——除非你打算把它们当公开夹具，并且授权清楚。
