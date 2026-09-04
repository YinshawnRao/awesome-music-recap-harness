# 旗舰示例：TOP 榜倒数揭晓

竖屏盘点短视频的教学项目。看完根目录 [README](../../README.md) 再跟这个文件夹。

艺人 **北城** 和下面五首歌名都是**虚构占位**。它们不是必用的版权歌单。

**P1 用本机生成的合法占位竖屏**（色条 / 色块），不要去下载 `SOURCES.md` 里的 `example.com`。换成真实官方 URL 是后面的事。

## 1. 简报 — 你在做什么

先读 [`BRIEF.md`](BRIEF.md)。一句话：

> 北城 · 被低估的5首现场 · 竖屏 1080×1920 · 播放顺序 **N→1**（5→1）·
> 封面 / intro 不列歌单、不泄露第一名 · 配音 CV007

| 名次（播放顺序） | 歌名 | 表演者 | 标签 |
| --- | --- | --- | --- |
| 5（最先播） | 纸灯笼 | 北城 | placeholder |
| 4 | 夜渡 | 北城 | placeholder |
| 3 | 玻璃港 | 北城 | placeholder |
| 2 | 北窗 | 北城 | placeholder |
| 1（最后播） | 末班月台 | 北城 | placeholder |

素材：[`SOURCES.md`](SOURCES.md)。设计备注：[`design.md`](design.md)。

## 2. 你应该看到的目录

```text
examples/top-ranking-demo/
  BRIEF.md                 这期为什么存在
  SOURCES.md               P1=本地占位；以后再换官方 URL
  songs.json               N→1 播放列表
  project-manifest.json    schema v2 契约
  voice-selection.json     整期只用一个声音
  narration-request.json   TTS 批次
  narration/*.wav.tts.json sidecar（结构 VOICE 门禁够用）
  audio/                   P2 一句烟雾 WAV（gitignore；见 audio/README.md）
  publishing/xiaohongshu.md
  qa/                      FINAL 骨架落在这里
  package.json             hyperframes@0.6.69 版本钉
  footage/                 生成器输出 — 合法占位竖屏（gitignore）
  downloads/               你自己建 — yt-dlp 原始输出（gitignore）
  clips/                   加过黑边的竖屏；P1 生成器会写入（gitignore）
  renders/                 你自己建 — full.mp4 再成 <slug>.mp4（gitignore）
```

`footage/`、`downloads/`、`clips/`、`renders/`、`audio/*.wav` 里什么都不随仓库附带。

## 3. 命令（从仓库根目录）

### P1 — 生成本地占位竖屏（不联网）

不要下载版权 MV，也不要去拉 `example.com`：

```bash
python3 tools/video/make_placeholder_clips.py
# 或
python3 tools/cli.py placeholder-clips
```

默认给五条名次各写约 4 秒、1080×1920、可选短鸣：

- `examples/top-ranking-demo/footage/rank-0N.mp4`
- `examples/top-ranking-demo/clips/vert_rank-0N.mp4`（和 `songs.json` 的 `clip` 对上）

只要静音音轨：`--silent`。只要 `footage/`：`--footage-only`。

公开下载烟雾（另一条路径，不是这五首歌）：

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

只有改了简报，才重新解析配音或重新空跑旁白（见 [docs/runbook.md](../../docs/runbook.md)）。不要从那里起步。

### P2 — 真配音（Apple Silicon + 自录参考）

环境 + `reference.wav` 齐了之后，不要再加 `--dry-run`：

```bash
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate
# 一句 → audio/smoke.wav

python3 tools/cli.py smoke-narrate -- --full
# 再跑 narration-request.json → narration/*.wav
```

VOICE 两种模式：

| 模式 | 你有什么 | 命令 |
| --- | --- | --- |
| 结构 | 只有 sidecar | `verify_voice_usage.py` → `VOICE GATE: PASS mode=structure` |
| 真 WAV | sidecar + 旁白文件 | 同上并加 `--require-wav` → `VOICE GATE: PASS mode=wav` |

安装、录音、缺权重时的中文下一步：[docs/mac-setup.md](../../docs/mac-setup.md)、[voices/local/README.md](../../tools/tts/voices/local/README.md)。不要改用 Kokoro。

### 以后：有了真实 URL + 真实 Cookie

1. 把 `SOURCES.md` 里每一行 `example.com` 换成你有权使用的素材。
2. 确认 `python3 tools/video/check_yt_cookie.py` 打印
   `static preflight: PASS`（不是还带着占位符的示例）。
3. 下载**只**走封装：

   ```bash
   python3 tools/video/yt_dlp_readonly.py -- "<YOUR_URL>" \
     -o "examples/top-ranking-demo/downloads/%(id)s.%(ext)s"
   ```

4. 每条片段用 `vfill.sh`（裁切带铺满宽度）加黑边，输出到 `clips/vert_rank-0N.mp4`。
5. 生成旁白 WAV：`python3 tools/cli.py smoke-narrate -- --full`（P2；不要 `--dry-run`）。
6. 进本目录，锁版本渲染再 mux（**P3**）：

   ```bash
   npm run render
   ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a \
     -c:v copy -c:a aac -b:a 192k -shortest renders/top-ranking-demo.mp4
   ```

`npm run render` 就是 `npx --yes hyperframes@0.6.69 render --output renders/full.mp4 --sdr`。

## 4. 门禁 — PASS 长什么样

| 门禁 | 命令 | 成功那一行（工具原文） |
| --- | --- | --- |
| VOICE | `verify_voice_usage.py` | `VOICE GATE: PASS mode=structure`（有 WAV 再加 `--require-wav` → `mode=wav`） |
| PROJECT | `verify_project.py` | `PROJECT CONTRACT: PASS mode=structure` |
| PUBLISHING | `verify_publishing.py` | `PUBLISHING COPY: PASS` |
| FINAL | `prepare_final_qa.py` | `FINAL VIDEO QA: PASS skeleton pending_machine_qa` |

v1 的 FINAL 只写待审骨架。它不证明画面或 ASR。

## 5. 做完

- **P1：** 占位竖屏 + 上面四行结构门禁。
- **P2 今天：** `audio/smoke.wav` 或 `narration/*.wav` + `VOICE GATE: PASS mode=wav`。
- **成片文件：** `renders/top-ranking-demo.mp4` + `publishing/xiaohongshu.md`。
  后面阶段需要你的 Cookie、网络和有授权的素材。
