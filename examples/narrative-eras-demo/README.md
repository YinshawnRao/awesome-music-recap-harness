# 编年脚手架：南港的三个时期

这不是榜单。`project_kind` 是 **`narrative`**：按时间线讲三个阶段，条目**没有 `rank`**，封面也不必保「第一名」悬念。

虚构艺人 **南港** 和下面三首歌名都是占位。它们不是必用的版权歌单，也不附带画面文件。

**旗舰可跑通路径仍是** [`examples/top-ranking-demo/`](../top-ranking-demo/)（N→1 + `smoke-e2e`）。本目录只证明：叙事契约、配音 sidecar、小红书文案能过结构门禁。P4 **不**为叙事提交 HyperFrames 合成，也不提供 `smoke-e2e`。

## 和 TOP 榜差在哪

| | TOP 教学项目 | 本编年脚手架 |
| --- | --- | --- |
| `project_kind` | `top_ranking` | `narrative` |
| 播放顺序 | 名次 N→1，封面 / intro 保悬念 | 时间线：早期 → 中段 → 江边 |
| 条目 | 必须有 `rank` | **禁止**写 `rank` |
| 成片 | `python3 tools/cli.py smoke-e2e` | 先抄结构；真渲染请回到榜单教学项目 |
| 倒数计划 | `countdown_build.py --plan-only` | 不要跑；那是榜单规划器 |

配音、双平台取材声明、发布文案、mux 规则和榜单相同。红线见 [CONVENTIONS.md](../../CONVENTIONS.md)。形态说明：[docs/beyond-the-demo.md](../../docs/beyond-the-demo.md)。

## 1. 简报

先读 [`BRIEF.md`](BRIEF.md)。一句话：

> 南港 · 三个时期的现场 · 竖屏 1080×1920 · **编年顺序**（不是倒数）· 配音 CV007

| 时期（播放顺序） | 歌名 | 表演者 | 标签 |
| --- | --- | --- | --- |
| 早期（最先播） | 旧收音机 | 南港 | placeholder |
| 中段 | 末班路灯 | 南港 | placeholder |
| 江边（最后播） | 江面回声 | 南港 | placeholder |

素材占位：[`SOURCES.md`](SOURCES.md)。

## 2. 你应该看到的目录

```text
examples/narrative-eras-demo/
  BRIEF.md                 这期为什么存在、和榜单有何不同
  SOURCES.md               example.com 占位；不要下载
  songs.json               时间线列表（没有 rank）
  project-manifest.json    schema v2，project_kind=narrative
  voice-selection.json     整期只用一个声音
  narration-request.json   TTS 批次
  narration/*.wav.tts.json sidecar（结构 VOICE 门禁够用）
  publishing/xiaohongshu.md
  timeline.json            编年骨架（给 FINAL 预备）
  qa/                      FINAL 骨架落在这里
```

没有 `index.html` / `package.json` / 占位竖屏生成器。要看画面闭环，去 TOP 教学项目。

## 3. 结构门禁（从仓库根目录）

不需要 Cookie、不需要片段、不需要 TTS 模型：

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/narrative-eras-demo/voice-selection.json \
  --project-root examples/narrative-eras-demo

python3 tools/video/verify_project.py --project examples/narrative-eras-demo
python3 tools/video/verify_publishing.py --project examples/narrative-eras-demo
python3 tools/video/prepare_final_qa.py --project examples/narrative-eras-demo
```

预期：

```text
VOICE GATE: PASS mode=structure
PROJECT CONTRACT: PASS mode=structure
PUBLISHING COPY: PASS
FINAL VIDEO QA: PASS skeleton pending_machine_qa
```

不要对这个目录跑 `countdown_build.py`（它要求 N→1 名次）。不要对这个目录跑 `smoke-e2e`（它要榜单合成文件）。

真配音、真下载、真渲染：先走通 [TOP 教学项目](../top-ranking-demo/README.md)，再按 [docs/runbook.md](../../docs/runbook.md) 抄目录。叙事转场目标 6–8 秒，WAV 硬上限 10 秒（榜单转场是 4–6 / 8）。文案规则：[docs/publishing.md](../../docs/publishing.md)。
