# 本地参考 WAV（不进 git）

教学项目默认声槽是 **CV007（低沉纪实）**。

仓库**不**附带任何人的声音。你自己录大约 10 秒，装到本目录之后才能真配音。

## 放哪里

```text
tools/tts/voices/local/CV007/reference.wav
```

这个路径已被 gitignore。不要提交真实 WAV。

装进去：

```bash
python3 tools/tts/install_reference.py ~/Desktop/reference.wav
# 默认 --voice CV007
```

换声槽：`--voice CV001`（会写成 `local/CV001/reference.wav`）。

## 怎么录

1. **安静房间。** 关掉风扇、音乐、电视、空调出风。手机开飞行模式。
2. **距离。** 嘴离麦克风大约 15–20cm，正常说话。不要贴麦气声，也不要喊。
3. **格式。** 导出 **单声道 16-bit PCM WAV**。不要把 m4a / mp3 当最终文件（`install_reference.py` 在装了 ffmpeg 时可以转一次）。
4. **长度。** 目标 **约 10 秒**。8–15 秒都能用；短于 3 秒或长于 45 秒会失败。
5. **读这句**（和 `voices/registry.json` 的 `reference_text` 对齐）：

> 你好，我是本期的声音候选。今天我们一起听听，这种角色声线放进视频解说，会是什么感觉。

QuickTime：文件 → 新建音频录制 → 停止 → 导出为 WAV。

或（本机麦克风）：

```bash
ffmpeg -f avfoundation -i ":0" -t 10 -ac 1 -ar 24000 -c:a pcm_s16le ~/Desktop/reference.wav
```

只看说明：

```bash
python3 tools/tts/install_reference.py --print-tips
```

## 下一步

```bash
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate
```

缺权重或 Metal 时，命令会用中文告诉你下一步。**不要改用 Kokoro。**
