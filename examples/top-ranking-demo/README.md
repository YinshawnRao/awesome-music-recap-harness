# 教学示例：榜单倒数揭晓

竖屏盘点短视频的教学示例，也是仓库里**唯一一条能 `smoke-e2e` 出片**的路径。请先读根目录 [README](../../README.md)，再对照本目录。本地 AI Agent 请同时遵守 [AGENTS.md](../../AGENTS.md)。

艺人 **北城** 和下面五首歌名都是**虚构占位**，不是必用的版权歌单。

**使用本机生成的合法占位竖屏**（色条 / 色块），不要下载 `SOURCES.md` 里的 `example.com`。换成真实官方 URL 是后续步骤。

不是榜单、要按时间线讲述时，编年脚手架在 [`examples/narrative-eras-demo/`](../narrative-eras-demo/)（只有结构，没有合成）。

## 1. 简报

先读 [`BRIEF.md`](BRIEF.md)。本期概要：

> 北城 · 被低估的5首现场 · 竖屏 1080×1920 · 按名次从低到高揭晓（末位先播，首位最后）·
> 封面 / intro 不列歌单、不泄露第一名 · 配音 CV007

| 名次（播放顺序） | 歌名 | 表演者 | 标签 |
| --- | --- | --- | --- |
| 5（最先播） | 纸灯笼 | 北城 | placeholder |
| 4 | 夜渡 | 北城 | placeholder |
| 3 | 玻璃港 | 北城 | placeholder |
| 2 | 北窗 | 北城 | placeholder |
| 1（最后播） | 末班月台 | 北城 | placeholder |

素材：[`SOURCES.md`](SOURCES.md)。设计备注：[`design.md`](design.md)。

## 2. 目录结构

```text
examples/top-ranking-demo/
  BRIEF.md                 本期简报
  SOURCES.md               本地占位；之后再换官方 URL
  songs.json               按名次从低到高排列的播放列表
  project-manifest.json    schema v2 契约
  voice-selection.json     整期只用一个声音
  narration-request.json   TTS 批次
  narration/*.wav.tts.json sidecar（结构 VOICE 门禁够用）
  audio/                   单句试生成 WAV（gitignore；见 audio/README.md）
  publishing/xiaohongshu.md
  qa/                      FINAL 骨架落在这里
  package.json             hyperframes@0.6.69 版本钉
  index.html               竖屏合成（1080×1920，已提交）
  styles.css / composition.js
  smoke-timeline.json      连通性验证时长（30s）；正式片长仍看 timeline.json
  footage/                 生成器输出 — 合法占位竖屏（gitignore）
  downloads/               本机自建 — yt-dlp 原始输出（gitignore）
  clips/                   加过黑边的竖屏；占位生成器会写入（gitignore）
  renders/                 smoke-e2e 写出 full.mp4 再成 <slug>.mp4（gitignore）
```

`footage/`、`downloads/`、`clips/`、`renders/`、`audio/*.wav` 里的内容不随仓库附带。

## 3. 命令（从仓库根目录）

### 生成本地占位竖屏（不联网）

不要下载版权 MV，也不要拉取 `example.com`：

```bash
python3 tools/video/make_placeholder_clips.py
# 或
python3 tools/cli.py placeholder-clips
```

默认给五条名次各写约 4 秒、1080×1920、可选短鸣：

- `examples/top-ranking-demo/footage/rank-0N.mp4`
- `examples/top-ranking-demo/clips/vert_rank-0N.mp4`（和 `songs.json` 的 `clip` 对上）

只要静音音轨：`--silent`。只要 `footage/`：`--footage-only`。

公开下载连通性验证（另一条路径，不是这五首歌）：

```bash
python3 tools/cli.py smoke-download
```

### 第一次跑通 — 只验结构

不需要 Cookie、不需要片段、不需要 TTS 模型：

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo

python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo
```

只有改了简报，才重新解析配音或重新空跑旁白（见 [docs/runbook.md](../../docs/runbook.md)）。制作下一期盘点时再打开 runbook；第一次跑通不必从那里开始。

### 真配音（可选；Apple Silicon + 自录参考）

环境与 `reference.wav` 齐备之后，不要再加 `--dry-run`：

```bash
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate
# 单句 → audio/smoke.wav

python3 tools/cli.py smoke-narrate -- --full
# 再跑 narration-request.json → narration/*.wav
```

VOICE 两种模式：

| 模式 | 条件 | 命令 |
| --- | --- | --- |
| 结构 | 只有 sidecar | `verify_voice_usage.py` → `VOICE GATE: PASS mode=structure` |
| 真 WAV | sidecar + 旁白文件 | 同上并加 `--require-wav` → `VOICE GATE: PASS mode=wav` |

安装、录音、缺权重时的中文下一步：[docs/mac-setup.md](../../docs/mac-setup.md)、[voices/local/README.md](../../tools/tts/voices/local/README.md)。不要改用 Kokoro。

### 一条命令出竖屏成片

不需要真 Cookie，也不需要 Qwen。没有旁白 WAV 就铺静音床（加 `--tone` 改轻正弦）：

```bash
python3 tools/cli.py smoke-e2e
```

产出（均 gitignore）：

- `master.wav` — 有 `narration/*.wav` 就预混；否则静音 / 轻正弦
- `renders/full.mp4` — HyperFrames 0.6.69 `--sdr`
- `renders/top-ranking-demo.mp4` — mux 后的可播放竖屏

**完成状态：** 能播放的竖屏 mp4，画面可为色条占位。FINAL 仍是待审骨架。

Linux 没有 Chrome 时会失败并打印中文下一步。只验已提交的合成文件：

```bash
python3 tools/cli.py smoke-e2e -- --structure-only
```

两条音轨路径：

| 条件 | master.wav | 成片能否播放 |
| --- | --- | --- |
| `narration/*.wav`（P2） | 按 `smoke-timeline.json` 预混旁白 | 能，带口播 |
| 只有 sidecar | 静音床；`--tone` 则轻正弦 | 能播放，仅用于验证画面闭环，不是可发布成片 |

### 后续：有了真实 URL 与真实 Cookie

1. 把 `SOURCES.md` 里每一行 `example.com` 换成有权使用的素材。
2. 确认 `python3 tools/video/check_yt_cookie.py` 打印
   `static preflight: PASS`（不是还带着占位符的示例）。
3. 下载**只**走封装：

   ```bash
   python3 tools/video/yt_dlp_readonly.py -- "<YOUR_URL>" \
     -o "examples/top-ranking-demo/downloads/%(id)s.%(ext)s"
   ```

4. 每条片段用 `vfill.sh`（裁切带铺满宽度）加黑边，输出到 `clips/vert_rank-0N.mp4`。
5. 生成旁白 WAV：`python3 tools/cli.py smoke-narrate -- --full`（P2；不要 `--dry-run`）。
6. 成片优先走一条命令：`python3 tools/cli.py smoke-e2e`。
   分步也可以：`vfill.sh`（真素材才需要加黑边）→ 项目目录 `npm run render` → mux。

`npm run render` 就是 `npx --yes hyperframes@0.6.69 render --output renders/full.mp4 --sdr`。

## 4. 门禁 — PASS 字面

| 门禁 | 命令 | 成功那一行（工具原文） |
| --- | --- | --- |
| VOICE | `verify_voice_usage.py` | `VOICE GATE: PASS mode=structure`（有 WAV 再加 `--require-wav` → `mode=wav`） |
| PROJECT | `verify_project.py` | `PROJECT CONTRACT: PASS mode=structure` |
| PUBLISHING | `verify_publishing.py` | `PUBLISHING COPY: PASS` |
| FINAL | `prepare_final_qa.py` | `FINAL VIDEO QA: PASS skeleton pending_machine_qa` |

v1 的 FINAL 只写待审骨架。它不证明画面或 ASR。

## 5. 完成标准

- 占位竖屏 + 上面四行结构门禁。
- 可选：`audio/smoke.wav` 或 `narration/*.wav` + `VOICE GATE: PASS mode=wav`。
- `renders/top-ranking-demo.mp4`（色条亦可）+ `publishing/xiaohongshu.md`。
  换成真素材 / 真 Cookie 是后续步骤。文案规则见 [docs/publishing.md](../../docs/publishing.md)。
