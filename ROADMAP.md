# 路线图：开箱即用

目标：陌生人 clone 之后，能做出一条竖屏榜单短视频。分四期，不一次做完。

人从根目录 [README](README.md) 和 [`examples/top-ranking-demo/`](examples/top-ranking-demo/) 开始。本页只讲阶段边界。

## P1 素材 / 下载烟雾（本阶段）

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

## P2 配音

**目标：** 教学项目能出旁白 WAV，VOICE 门禁对真文件变绿。

预期：Qwen / MLX 安装可跟做、`reference.wav` 就位、去掉 `--dry-run`。不在 P1 做安装自动化。

## P3 渲染成片 smoke-e2e

**目标：** 占位片段 + 旁白能走完 HyperFrames 0.6.69 `--sdr` → mux → `renders/<slug>.mp4`。

预期：一条可播放的竖屏成片（画面可以是色条）。不在 P1 做完整 HTML 渲染。

## P4 交付与扩展

**目标：** 发布文案、可选网盘、教学项目之外的形态。

预期：小红书文案打磨、`tools/delivery/baidu/` 可选插件、`docs/beyond-the-demo.md` 里的其他 `project_kind`。不在 P1 做。

## 阶段对照

| 阶段 | 陌生人能证明什么 | 明确不做 |
| --- | --- | --- |
| P1 | Cookie 路径 + 公开下载烟雾 + 本地占位竖屏 | 版权 MV、真配音、成片 |
| P2 | 真旁白 WAV | 成片渲染 |
| P3 | 一条可播放的竖屏 mp4 | 网盘、其他形态 |
| P4 | 能发出去、能换形态 | — |
