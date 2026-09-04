# 路线图：开箱即用

目标：陌生人 clone 之后，能做出一条竖屏榜单短视频。分四期，不一次做完。

人从根目录 [README](README.md) 和 [`examples/top-ranking-demo/`](examples/top-ranking-demo/) 开始。本页只讲阶段边界。

P1–P4 全部完成之前，本文件会一直留着。

## P1 素材 / 下载烟雾 ✅ 已完成

**目标：** 素材闭环能跑。不随仓库分发版权 MV。

做成：

- Cookie 最短安装：拷示例 → `chmod 0600` → 打印导出步骤（不打印密钥）
- 公开 YouTube 烟雾下载（Jawed Karim《Me at the zoo》，`jNQXAC9IVRw`）
- 教学项目五条合法占位竖屏（ffmpeg 色条 / 色块，可加短鸣）
- 结构门禁照旧 PASS

不包含：真配音、HyperFrames 成片、百度网盘。

怎么验（Mac，`brew install ffmpeg yt-dlp` 之后）：

```bash
bash tools/video/install_cookies.sh
python3 tools/cli.py smoke-download
python3 tools/video/make_placeholder_clips.py
```

`smoke-download` 要么拉下公开样本，要么打印可执行的 Cookie 修复。占位片段生成不联网。

## P2 配音 ✅ 已完成

**目标：** 教学项目能出旁白 WAV，VOICE 门禁对真文件变绿。

做成：

- Mac / Apple Silicon 可复制安装：`bash tools/tts/bootstrap_mac.sh` + `python3 tools/tts/setup_check.py`
- 开箱默认：用户自录约 10 秒 `reference.wav`，装进 CV007 本地声槽（gitignore）
- `smoke-narrate`：先体检，再生成一句短旁白；`--full` 再跑整批教学旁白
- VOICE 分两种：`mode=structure`（sidecar）和 `mode=wav`（`--require-wav`）

诚实边界：Qwen 权重不随仓库分发。缺 Metal / 缺 `AMRH_QWEN_*` / 缺参考 → 中文下一步后失败。**不要改用 Kokoro。**

怎么验（M 系列 Mac，合法权重 + 自录参考齐了之后）：

```bash
bash tools/tts/bootstrap_mac.sh
source tools/tts/runtime/env.sh
# 按 docs/mac-setup.md 下载权重并 export AMRH_QWEN_BASE_MODEL
python3 tools/tts/install_reference.py ~/Desktop/reference.wav
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate
```

没有权重时，后两条必须失败并打印中文下一步，而不是堆栈。

## P3 渲染成片 smoke-e2e（本阶段）

**目标：** 占位片段 +（可选）旁白走完 HyperFrames 0.6.69 `--sdr` → mux → `renders/<slug>.mp4`。

做成：

- 教学项目提交竖屏 1080×1920 HTML / CSS / JS（N→1，五条占位，封面 / intro / outro / CTA）
- 只锁 `hyperframes@0.6.69`；渲染加 `--sdr`，工人数走 `resource_budget.py`
- 有旁白 WAV 就预混 `master.wav`；没有就静音床或 `--tone` 轻正弦，照样 mux
- 一条命令：`python3 tools/cli.py smoke-e2e`
- Linux 没有 Chrome 时失败并打印中文下一步；结构已齐，Mac 可渲

怎么验（Mac，brew + Node 22 + Chrome）：

```bash
python3 tools/cli.py smoke-e2e
# 没有 Chrome 的机器：
python3 tools/cli.py smoke-e2e -- --structure-only
```

做完：`examples/top-ranking-demo/renders/top-ranking-demo.mp4` 可播放（画面可以是色条）。mp4 不进 git。FINAL 仍是待审骨架。

## P4 交付与扩展

**目标：** 发布文案、可选网盘、教学项目之外的形态。

预期：小红书文案打磨、`tools/delivery/baidu/` 可选插件、`docs/beyond-the-demo.md` 里的其他 `project_kind`。不在 P3 做。

## 阶段对照

| 阶段 | 陌生人能证明什么 | 明确不做 |
| --- | --- | --- |
| P1 ✅ | Cookie 路径 + 公开下载烟雾 + 本地占位竖屏 | 版权 MV、真配音、成片 |
| P2 ✅ | 真旁白 WAV | 成片渲染 |
| P3（当前） | 一条可播放的竖屏 mp4（占位画面也可以） | 网盘、其他形态 |
| P4 | 能发出去、能换形态 | — |
