# awesome-music-recap-harness

面向中文创作者的开源音乐盘点工作台：选题、YouTube 与 B 站取材、旁白配音、竖屏短视频合成，以及发布文案校验。

本页是可复现操作入口，不是内部实现说明。请先读本页与 [`examples/top-ranking-demo/`](examples/top-ranking-demo/)。用本地 AI Agent 驱动时，见下方「在本地 AI Agent 中运行」与 [`AGENTS.md`](AGENTS.md)。协议：**MIT**。成片渲染与真配音以 **Mac** 为主。

[![结构门禁](https://github.com/YinshawnRao/awesome-music-recap-harness/actions/workflows/structure-gates.yml/badge.svg)](https://github.com/YinshawnRao/awesome-music-recap-harness/actions/workflows/structure-gates.yml)

## 当前能力

克隆仓库后，本机可以完成：

- **取材**：安装 Cookie、对公开 YouTube 样本做连通性验证（冒烟测试）、为教学示例生成本机合法占位竖屏
- **配音（可选）**：Apple Silicon + 自录参考音 + 自备 Qwen 权重，生成旁白 WAV
- **成片**：`smoke-e2e` 渲染竖屏 mp4（无旁白时使用静音床；画面可为色条占位）
- **发布**：小红书文案门禁校验；可选将成片上传至百度网盘（凭证不进仓库）
- **其他形态**：榜单倒数揭晓是默认可复现路径（按名次从低到高播放：末位先播，首位最后）；编年 / 叙事见 [`examples/narrative-eras-demo/`](examples/narrative-eras-demo/)

素材、模型权重、配音母带与**真实 Cookie 均不随仓库分发**。教学画面使用本机生成的合法占位竖屏，不附带版权 MV。

| GitHub Actions 覆盖 | 仍须本机 Mac |
| --- | --- |
| `pytest`、四道结构门禁、`smoke-e2e --structure-only`、叙事脚手架门禁、百度 `--dry-run` | Chrome 渲染、Qwen 真配音、真实 Cookie 下载、可播放成片 |

## 适用场景

用于制作榜单盘点竖屏短视频：按名次从低到高揭晓（末位先播，首位最后），并具备一台已安装 Homebrew 的 Mac。首次使用不必掌握全部工具。仅校验结构、不渲染时，Linux 亦可。

## 交付物

- 教学示例：虚构艺人 **北城**、五首带标签的占位曲目（非真实版权歌单）
- 受控的 Cookie 下载路径（渲染真实成片须使用真实 Cookie）
- 四道门禁，用于确认项目结构完整
- 明确的完成产物：`renders/<slug>.mp4` 与小红书文案

## 在本地 AI Agent 中运行

多数制作现在由本地 AI Agent 驱动，而不是逐条在终端里执行命令。把本仓库放到 **Cursor、Claude Code、Codex、Windsurf** 或同类工具里打开，让 Agent 按契约执行。人类操作入口仍是本页；Agent 的工作契约是 [`AGENTS.md`](AGENTS.md)（Claude Code 若加载 [`CLAUDE.md`](CLAUDE.md)，它只指向同一份契约）。制作红线见 [`CONVENTIONS.md`](CONVENTIONS.md)。

人类仍须自行准备下列输入，Agent 不能从仓库里变出来：

- 真实 Netscape Cookie（仓库根目录 `all_cookies.txt`，权限 `0600`；不要提交）
- 有权使用的素材 URL（教学示例用本机占位竖屏，不要下载 `example.com`）
- 真配音：Apple Silicon Mac 上的合法 Qwen 权重 + 自录参考 WAV

没有这些输入时，Agent 应停在对应步骤，并继续可做的结构门禁。Linux 上通常只能跑到结构 PASS；可播放竖屏与真配音仍以 Mac 为准。

把下面整段发给 Agent 作为第一条指令：

```text
请先阅读本仓库的 AGENTS.md（工作契约）、README.md、CONVENTIONS.md，以及 tools/tts/README.md 与 tools/video/README.md。然后按 examples/top-ranking-demo/ 走默认可复现路径：先跑结构门禁，再在环境允许时执行 python3 tools/cli.py smoke-e2e（无 Chrome 则改为 --structure-only）。向我回报已读文件、已执行命令、四道门禁的字面结果、成片路径（renders/top-ranking-demo.mp4）或停步原因与下一步。不要提交 Cookie、模型权重、配音母带或版权素材；缺 Qwen 时不要改用 Kokoro。
```

## 1. 安装（Mac）

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

HyperFrames **必须锁定 0.6.69**。不要使用 `@latest`。

仅做结构门禁、不渲染时，安装 `python3` 与 `ffmpeg` 即可，不必安装 Chrome 或 Qwen。

## 2. Cookie

仓库根目录若没有权限为 `0600` 的 `all_cookies.txt`，`yt_dlp_readonly.py` 不会开始下载。§6 的结构走查不需要真实登录。

```bash
bash tools/video/install_cookies.sh
```

这一步只拷贝**假的**格式模板（`PLACEHOLDER_NOT_A_SESSION_*`），并打印下一步。不要提交 `all_cookies.txt`。

**从浏览器导出一份真实的 Netscape Cookie 文件**（同一配置里登录 YouTube/Google **和** B 站）。原始导出先存到仓库外，再覆盖：

```bash
python3 tools/video/filter_cookie_jar.py "$HOME/Downloads/raw-cookies.txt" \
  --output "$HOME/Downloads/candidate-cookies.txt"
cp "$HOME/Downloads/candidate-cookies.txt" all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

公开 YouTube 样本在部分网络可以不登录就下载；**B 站和完整教学下载仍必须换成真实导出**。下载只走 `tools/video/yt_dlp_readonly.py`。更细的说明：[examples/cookies/README.md](examples/cookies/README.md)。

## 3. 占位竖屏与下载连通性

```bash
# 公开 YouTube 连通性验证（Me at the zoo / jNQXAC9IVRw）。缺 jar 会打印安装步骤。
python3 tools/cli.py smoke-download

# 为教学示例生成五条合法占位竖屏（不联网、不是版权 MV）
python3 tools/video/make_placeholder_clips.py
```

连通性验证输出：`examples/smoke-download/out/`（gitignore）。占位片段：`examples/top-ranking-demo/footage/` 和 `clips/vert_rank-0N.mp4`。选用这条公开视频的原因、以及 Cookie 缺失时的行为：见 [examples/smoke-download/README.md](examples/smoke-download/README.md)。

## 4. 配音（可选）

结构门禁不需要这一节。要生成**真实 WAV**，在 M 系列 Mac 上按顺序执行。权重与参考音均不随仓库分发。

```bash
# 1）建独立 Qwen 解释器（不下载权重）
bash tools/tts/bootstrap_mac.sh
source tools/tts/runtime/env.sh

# 2）合法下载 Qwen3-TTS Base 8-bit 到本机，再 export
#    模型卡与钉 revision：docs/mac-setup.md
export AMRH_QWEN_BASE_MODEL="$HOME/amrh-models/Qwen3-TTS-12Hz-0.6B-Base-8bit"

# 3）自录约 10 秒单声道 WAV，装进教学声槽 CV007（gitignore）
python3 tools/tts/install_reference.py ~/Desktop/reference.wav

# 4）缺任何一项都会用中文说明下一步；不会改用 Kokoro
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate
```

单句试生成：`examples/top-ranking-demo/audio/smoke.wav`。整批教学旁白：

```bash
python3 tools/cli.py smoke-narrate -- --full
```

录音要点和路径：[tools/tts/voices/local/README.md](tools/tts/voices/local/README.md)。完整步骤：[docs/mac-setup.md](docs/mac-setup.md)。

## 5. 一条命令出片

装好 ffmpeg + Node 22 + Chrome 之后，在仓库根目录：

```bash
python3 tools/cli.py smoke-e2e
```

它会：没有占位竖屏就生成本机色条 → 有旁白 WAV 就预混 `master.wav`，没有就铺静音床（加 `--tone` 改轻正弦）→ `hyperframes@0.6.69 render --sdr` → mux 到 `examples/top-ranking-demo/renders/top-ranking-demo.mp4`（gitignore）→ 再跑结构门禁。

**完成状态：** 一条可播放的竖屏 mp4。画面可为色条占位。无真配音亦可出片（静音床或轻正弦），该结果仅用于验证渲染闭环，不可作为发布成片。

Linux CI 常常没有 Chrome：命令会失败，并用中文写出下一步。合成文件（HTML / CSS / JS / `package.json`）已经提交，请到 Mac 上渲染。

只要结构、不渲染（CI 也跑这一条）：

```bash
python3 tools/cli.py smoke-e2e -- --structure-only
```

## 6. 教学示例：榜单倒数揭晓

在仓库根目录执行。教学示例已经带好选题简报、配音选择、清单、旁白 sidecar 和小红书文案。此步确认**结构可走通**：

```bash
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo

python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo
```

预期输出（工具原文为英文，须与下列字面一致）：

```text
VOICE GATE: PASS mode=structure
PROJECT CONTRACT: PASS mode=structure
PUBLISHING COPY: PASS
FINAL VIDEO QA: PASS skeleton pending_machine_qa
```

目录说明、选题简报，以及后续的下载 / 渲染步骤，见 [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md)。

## 7. 完成标准

| 本机状态 | 说明 |
| --- | --- |
| 占位竖屏 + 四道结构门禁 PASS | 不需要 Cookie / Qwen / Chrome |
| 自录参考 + 合法 Qwen 权重 → 真旁白 WAV | `setup_check` / `smoke-narrate`；齐备之后 `VOICE GATE: PASS mode=wav` |
| `renders/top-ranking-demo.mp4`（占位竖屏亦可） | `smoke-e2e`；FINAL 仍是待审骨架，不证明画面 / ASR |
| 小红书文案 | `publishing/xiaohongshu.md` 已过门禁 |
| 真正的盘点成片 | 换成有权使用的素材 + 真 Cookie + 真 WAV + 同一条 mux |

真版权成片需要：**本机有权使用的**素材 URL（替换 `SOURCES.md` 里的 `example.com`）、**真实** Cookie、旁白 WAV。先用占位片段证明渲染闭环，不要去下载 `example.com`。

分目录的完整命令：见 [教学示例 README](examples/top-ranking-demo/README.md)。

## 8. 常见问题

**Cookie 检查失败。** 缺 `all_cookies.txt`、权限不是 `0600`、还留着 `PLACEHOLDER_*`，或导出里没有 YouTube/Google + B 站字段。先跑 `bash tools/video/install_cookies.sh`，导出真实 Netscape 文件，再跑 `python3 tools/video/check_yt_cookie.py`。不要自行执行 `yt-dlp --cookies`。

**找不到 `ffmpeg`。** `brew install ffmpeg`，新开一个终端。`which ffmpeg` 应指向 Homebrew 路径。

**`node -v` 低于 22。** HyperFrames 0.6.69 需要 Node 22+。用 Homebrew / fnm / nvm 升级后执行 `hash -r`，再看 `node -v`。

**HyperFrames 版本。** 只用 `npx --yes hyperframes@0.6.69 ...`。裸写 `npx hyperframes` 或 `@latest` 都不对。教学示例目录里的 `npm run lint` / `npm run render` 已经锁定 0.6.69。

**TTS 体检未通过 / 真配音失败。** 结构门禁看 `VOICE GATE: PASS mode=structure`（sidecar 即可）。真 WAV 看 `python3 tools/tts/setup_check.py`：缺 Apple Silicon、缺 `AMRH_QWEN_PYTHON` / `AMRH_QWEN_BASE_MODEL`、缺自录参考，都会用中文写出下一步。不要改用 Kokoro。见 [docs/mac-setup.md](docs/mac-setup.md)。

## 延伸阅读

下列文档供第一次跑通之后查阅。默认可复现路径仍是 TOP 教学示例。

| 目的 | 文档 |
| --- | --- |
| 教学示例（简报 → 目录 → 成片） | [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md) |
| 编年 / 叙事脚手架（不是榜单） | [examples/narrative-eras-demo/README.md](examples/narrative-eras-demo/README.md) |
| 小红书文案规则 | [docs/publishing.md](docs/publishing.md) |
| 可选：百度网盘上传 | [tools/delivery/baidu/README.md](tools/delivery/baidu/README.md) |
| Cookie 导出细节 | [examples/cookies/README.md](examples/cookies/README.md) |
| 公开下载连通性验证 | [examples/smoke-download/README.md](examples/smoke-download/README.md) |
| 本地参考 WAV（gitignore） | [tools/tts/voices/local/README.md](tools/tts/voices/local/README.md) |
| Mac TTS / 额外安装 | [docs/mac-setup.md](docs/mac-setup.md) |
| 制作下一期盘点 | [docs/runbook.md](docs/runbook.md) |
| 流水线分层说明 | [docs/architecture.md](docs/architecture.md) |
| 其他节目形态、硬素材门禁 | [docs/beyond-the-demo.md](docs/beyond-the-demo.md) |
| CI 和本机分别做什么 | [docs/ci.md](docs/ci.md) |
| 制作红线 | [CONVENTIONS.md](CONVENTIONS.md) |
| 本地 AI Agent 工作契约 | [AGENTS.md](AGENTS.md) |
| 次要文档目录 | [docs/README.md](docs/README.md) |
