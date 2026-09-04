# awesome-music-recap-harness

做竖屏音乐盘点短视频的工作台：选歌、从 YouTube + B 站取材、配音、合成、发小红书。

这是一份**能跟着做完的指南**，不是内部实现说明书。先看本页和 [`examples/top-ranking-demo/`](examples/top-ranking-demo/)。协议：**MIT**。v1 **以 Mac 为主**。

四期开箱即用：[ROADMAP.md](ROADMAP.md)。**本仓库现在是 P2：配音闭环能跑。** P1（Cookie / 下载烟雾 / 占位竖屏）已完成。

## 适合谁

你要做一份榜单盘点（TOP / 倒数揭晓，播放顺序 **N→1**），手头有一台装了 Homebrew 的 Mac。第一天不必把所有工具都学完。

## 你会得到什么

- 教学项目：虚构艺人 **北城**、五首带标签的占位歌（不是真实版权歌单）
- 安全的 Cookie 下载路径（要渲成真成片，必须有真实 Cookie）
- 四道门禁，用来确认结构是否站得住
- 明确的「做完」产物：`renders/<slug>.mp4` + 小红书文案

素材、模型权重、配音母带、**真实 Cookie 都不随仓库分发**。P1 用本机生成的合法占位竖屏，不附带版权 MV。

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

## 2. Cookie（最短路径）

仓库根目录没有 `all_cookies.txt`（权限 `0600`），`yt_dlp_readonly.py` 不会开始下载。§4 的结构走查不需要真实登录。

```bash
bash tools/video/install_cookies.sh
```

这一步只拷**假的**格式模板（`PLACEHOLDER_NOT_A_SESSION_*`），并打印下一步。不要提交 `all_cookies.txt`。

**从浏览器导出一份真实的 Netscape Cookie 文件**（同一配置里登录 YouTube/Google **和** B 站）。原始导出先存到仓库外，再覆盖：

```bash
python3 tools/video/filter_cookie_jar.py "$HOME/Downloads/raw-cookies.txt" \
  --output "$HOME/Downloads/candidate-cookies.txt"
cp "$HOME/Downloads/candidate-cookies.txt" all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

公开 YouTube 样本在部分网络可以不登录就下；**B 站和完整教学下载仍必须换成真实导出**。下载只走 `tools/video/yt_dlp_readonly.py`。更细的说明：[examples/cookies/README.md](examples/cookies/README.md)。

## 3. P1 素材闭环（brew 装好就能跑）

```bash
# 公开 YouTube 烟雾（Me at the zoo / jNQXAC9IVRw）。缺 jar 会打印怎么装。
python3 tools/cli.py smoke-download

# 给教学项目生成五条合法占位竖屏（不联网、不是版权 MV）
python3 tools/video/make_placeholder_clips.py
```

烟雾输出：`examples/smoke-download/out/`（gitignore）。占位片段：`examples/top-ranking-demo/footage/` 和 `clips/vert_rank-0N.mp4`。为什么用这条公开视频、Cookie 缺了会怎样：见 [examples/smoke-download/README.md](examples/smoke-download/README.md)。阶段边界：[ROADMAP.md](ROADMAP.md)。

## 4. P2 配音闭环（Apple Silicon + 自录参考）

结构门禁不需要这一节。要**真的 WAV**，在 M 系列 Mac 上按顺序复制。权重和你的声音都不随仓库分发。

```bash
# 1）建独立 Qwen 解释器（不下载权重）
bash tools/tts/bootstrap_mac.sh
source tools/tts/runtime/env.sh

# 2）合法下载 Qwen3-TTS Base 8-bit 到本机，再 export
#    模型卡与钉 revision：docs/mac-setup.md
export AMRH_QWEN_BASE_MODEL="$HOME/amrh-models/Qwen3-TTS-12Hz-0.6B-Base-8bit"

# 3）自录约 10 秒单声道 WAV，装进教学声槽 CV007（gitignore）
python3 tools/tts/install_reference.py ~/Desktop/reference.wav

# 4）缺任何一项都会用中文告诉你下一步；不会改用 Kokoro
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate
```

一句烟雾：`examples/top-ranking-demo/audio/smoke.wav`。整批教学旁白：

```bash
python3 tools/cli.py smoke-narrate -- --full
```

录音要点和路径：[tools/tts/voices/local/README.md](tools/tts/voices/local/README.md)。完整复制步骤：[docs/mac-setup.md](docs/mac-setup.md)。

## 5. 第一次跑通 — TOP 教学项目

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
VOICE GATE: PASS mode=structure
PROJECT CONTRACT: PASS mode=structure
PUBLISHING COPY: PASS
FINAL VIDEO QA: PASS skeleton pending_machine_qa
```

目录说明、选题简报、以及后面的下载 / 渲染步骤，见 [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md)。

## 6. 「做完」长什么样

| 阶段 | 你手上有什么 | 门禁 |
| --- | --- | --- |
| **P1** | Cookie 路径 + 公开下载烟雾 + 五条占位竖屏 + 结构门禁 | VOICE `mode=structure`、PROJECT、PUBLISHING、FINAL 骨架全部 **PASS** |
| **P2 今天** | 自录参考 + 合法 Qwen 权重 → 至少一句真旁白 WAV | `setup_check` / `smoke-narrate`；齐了之后 `VOICE GATE: PASS mode=wav` |
| **真正的盘点成片** | `examples/top-ranking-demo/renders/top-ranking-demo.mp4` 和 `publishing/xiaohongshu.md` | 还是这四道门禁；mux 之后再过发布门禁 |

真 mp4 需要：**你自己有权使用的**素材 URL（替换 `SOURCES.md` 里的 `example.com`）、**真实** Cookie、旁白 WAV，以及一份 HyperFrames 成片。P1 先用占位片段，不要去下 `example.com`。

素材齐了之后再渲染（P3）：

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

## 7. 常见问题（前 5 条）

**Cookie 检查失败。** 缺 `all_cookies.txt`、权限不是 `0600`、还留着 `PLACEHOLDER_*`，或导出里没有 YouTube/Google + B 站字段。先跑 `bash tools/video/install_cookies.sh`，导出真实 Netscape 文件，再跑 `python3 tools/video/check_yt_cookie.py`。不要自己跑 `yt-dlp --cookies`。

**找不到 `ffmpeg`。** `brew install ffmpeg`，新开一个终端。`which ffmpeg` 应指向 Homebrew 路径。

**`node -v` 低于 22。** HyperFrames 0.6.69 需要 Node 22+。用 Homebrew / fnm / nvm 升级后执行 `hash -r`，再看 `node -v`。

**HyperFrames 版本。** 只用 `npx --yes hyperframes@0.6.69 ...`。裸写 `npx hyperframes` 或 `@latest` 都不对。教学项目目录里的 `npm run lint` / `npm run render` 已经锁死 0.6.69。

**TTS 体检不绿 / 真配音失败。** 结构门禁看 `VOICE GATE: PASS mode=structure`（sidecar 即可）。真 WAV 看 `python3 tools/tts/setup_check.py`：缺 Apple Silicon、缺 `AMRH_QWEN_PYTHON` / `AMRH_QWEN_BASE_MODEL`、缺自录参考，都会用中文写出下一步。不要改用 Kokoro。见 [docs/mac-setup.md](docs/mac-setup.md)。

## 第一次跑通之后

不要从这里起步。P3–P4 见 [ROADMAP.md](ROADMAP.md)。

| 你想做什么 | 看哪篇 |
| --- | --- |
| 开箱即用四期 | [ROADMAP.md](ROADMAP.md) |
| 教学项目（简报 → 目录 → 成片） | [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md) |
| Cookie 导出细节 | [examples/cookies/README.md](examples/cookies/README.md) |
| 公开下载烟雾 | [examples/smoke-download/README.md](examples/smoke-download/README.md) |
| 本地参考 WAV（gitignore） | [tools/tts/voices/local/README.md](tools/tts/voices/local/README.md) |
| Mac TTS / 额外安装 | [docs/mac-setup.md](docs/mac-setup.md) |
| 自己做下一期盘点 | [docs/runbook.md](docs/runbook.md) |
| 流水线为什么这样分层 | [docs/architecture.md](docs/architecture.md) |
| 其他节目形态、百度网盘、硬素材门禁 | [docs/beyond-the-demo.md](docs/beyond-the-demo.md) |
| 制作红线 | [CONVENTIONS.md](CONVENTIONS.md) |
| 次要文档目录 | [docs/README.md](docs/README.md) |
