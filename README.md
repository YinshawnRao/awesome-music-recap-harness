# awesome-music-recap-harness

做竖屏音乐盘点短视频的工作台：选歌、从 YouTube + B 站取材、配音、合成、发小红书。

这是一份**能跟着做完的指南**，不是内部实现说明书。先看本页和 [`examples/top-ranking-demo/`](examples/top-ranking-demo/)。协议：**MIT**。v1 **以 Mac 为主**。

## 适合谁

你要做一份榜单盘点（TOP / 倒数揭晓，播放顺序 **N→1**），手头有一台装了 Homebrew 的 Mac。第一天不必把所有工具都学完。

## 你会得到什么

- 教学项目：虚构艺人 **北城**、五首带标签的占位歌（不是真实版权歌单）
- 安全的 Cookie 下载路径（要渲成真成片，必须有真实 Cookie）
- 四道门禁，用来确认结构是否站得住
- 明确的「做完」产物：`renders/<slug>.mp4` + 小红书文案

素材、模型权重、配音母带、**真实 Cookie 都不随仓库分发**。

## 1. 安装（Mac，直接复制）

```bash
brew install ffmpeg yt-dlp
# Node 22+（Homebrew node、fnm 或 nvm 均可）
node -v          # 需要 v22 或更新
python3 --version
ffmpeg -version | head -n 1
yt-dlp --version

npx --yes hyperframes@0.6.69 doctor
python3 tools/tts/doctor.py
```

HyperFrames **必须锁 0.6.69**。不要用 `@latest`。

## 2. Cookie（完整流程必做）

仓库根目录没有 `all_cookies.txt`（权限 `0600`），下载不会开始。§3 的结构走查不需要真实登录。

```bash
cp examples/cookies/all_cookies.example.txt all_cookies.txt
chmod 0600 all_cookies.txt
```

示例文件是**假的**（`PLACEHOLDER_NOT_A_SESSION_*`），不能当登录态用。

**从浏览器导出一份真实的 Netscape Cookie 文件**：同一浏览器配置里同时登录 YouTube/Google **和** B 站。用 `cookies.txt` 导出插件（例如 “Get cookies.txt LOCALLY”）。原始导出**先存到仓库外面**，再自己覆盖运行时文件：

```bash
# 原始导出和筛选结果都必须放在仓库外
python3 tools/video/filter_cookie_jar.py "$HOME/Downloads/raw-cookies.txt" \
  --output "$HOME/Downloads/candidate-cookies.txt"
cp "$HOME/Downloads/candidate-cookies.txt" all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

`check_yt_cookie.py` 从不打印 Cookie 值。占位符还在时它会**失败**——在装上真实导出之前，这是正常的。永远不要提交 `all_cookies.txt`。唯一允许调用 yt-dlp 的入口是 `tools/video/yt_dlp_readonly.py`（它会把 jar 拷到仓库外的临时快照，避免 yt-dlp 改写原文件）。

更细的导出说明：[examples/cookies/README.md](examples/cookies/README.md)。

## 3. 第一次跑通 — TOP 教学项目

在仓库根目录执行。教学项目已经带好选题简报、配音选择、清单、旁白 sidecar 和小红书文案。你现在要确认的是**结构能走通**：

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo

python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo
```

预期输出（工具原文就是英文）：

```text
VOICE GATE: PASS
PROJECT CONTRACT: PASS mode=structure
PUBLISHING COPY: PASS
FINAL VIDEO QA: PASS skeleton pending_machine_qa
```

目录说明、选题简报、以及后面的下载 / 渲染步骤，见 [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md)。

## 4. 「做完」长什么样

| 阶段 | 你手上有什么 | 门禁 |
| --- | --- | --- |
| **今天第一次跑通** | 结构 + 倒数计划，没有随仓库附带的成片 | VOICE、PROJECT、PUBLISHING、FINAL 骨架全部 **PASS** |
| **真正的盘点成片** | `examples/top-ranking-demo/renders/top-ranking-demo.mp4` 和 `publishing/xiaohongshu.md` | 还是这四道门禁；mux 之后再过发布门禁 |

真 mp4 需要：**你自己有权使用的**素材 URL（替换 `SOURCES.md` 里的 `example.com` 占位）、**真实** Cookie、旁白 WAV，以及一份 HyperFrames 成片。完整下载取决于你的 Cookie 和网络。教学项目不附带片段。

素材齐了之后再渲染：

```bash
# 下载只能走只读封装
python3 tools/video/yt_dlp_readonly.py -- "<YOUR_URL>" -o "examples/top-ranking-demo/downloads/%(id)s.%(ext)s"
# 加黑边、配音（不要再加 --dry-run）、HyperFrames 0.6.69 --sdr，然后：
ffmpeg -i examples/top-ranking-demo/renders/full.mp4 \
  -i examples/top-ranking-demo/master.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  examples/top-ranking-demo/renders/top-ranking-demo.mp4
```

分目录的完整命令：见 [教学项目 README](examples/top-ranking-demo/README.md)。

## 5. 常见问题（前 5 条）

**Cookie 检查失败。** 缺 `all_cookies.txt`、权限不是 `0600`、还留着 `PLACEHOLDER_*`，或导出里没有 YouTube/Google + B 站字段。先拷示例，导出真实 Netscape 文件，`chmod 0600`，再跑 `python3 tools/video/check_yt_cookie.py`。不要自己跑 `yt-dlp --cookies`。

**找不到 `ffmpeg`。** `brew install ffmpeg`，新开一个终端。`which ffmpeg` 应指向 Homebrew 路径。

**`node -v` 低于 22。** HyperFrames 0.6.69 需要 Node 22+。用 Homebrew / fnm / nvm 升级后执行 `hash -r`，再看 `node -v`。

**HyperFrames 版本。** 只用 `npx --yes hyperframes@0.6.69 ...`。裸写 `npx hyperframes` 或 `@latest` 都不对。教学项目目录里的 `npm run lint` / `npm run render` 已经锁死 0.6.69。

**TTS 体检不绿。** 结构门禁不需要生成 WAV。`--dry-run` / 已有的 `.wav.tts.json` sidecar 就够第一次跑通。真配音需要 Apple Silicon、合法的 Qwen/MLX 安装，以及你自己的 `reference.wav`——见 [docs/mac-setup.md](docs/mac-setup.md)。不要悄悄改用 Kokoro。

## 第一次跑通之后

不要从这里起步。

| 你想做什么 | 看哪篇 |
| --- | --- |
| 教学项目（简报 → 目录 → 成片） | [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md) |
| Cookie 导出细节 | [examples/cookies/README.md](examples/cookies/README.md) |
| Mac TTS / 额外安装 | [docs/mac-setup.md](docs/mac-setup.md) |
| 自己做下一期盘点 | [docs/runbook.md](docs/runbook.md) |
| 流水线为什么这样分层 | [docs/architecture.md](docs/architecture.md) |
| 其他节目形态、百度网盘、硬素材门禁 | [docs/beyond-the-demo.md](docs/beyond-the-demo.md) |
| 制作红线 | [CONVENTIONS.md](CONVENTIONS.md) |
| 次要文档目录 | [docs/README.md](docs/README.md) |
