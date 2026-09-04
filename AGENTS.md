# AGENTS.md

本文件是本地 AI Agent（Cursor Agent、Claude Code、Codex、Windsurf 等）的工作契约。人类操作入口仍是 [README.md](README.md)。Cursor / Claude Code 等工具会自动加载本文件；请按本文执行，不要另起一套互相冲突的规则。

若环境同时提供 `CLAUDE.md`，它只是指向本文的薄指针，规则以本文为准。

## 意图

帮操作者按 README 走完教学示例 `examples/top-ranking-demo/`：选题简报、合法取材、旁白、竖屏合成与发布文案校验。第一次任务只走这条默认可复现路径，不要一上来铺开全部 `project_kind` 或可选插件。其他形态见 [docs/beyond-the-demo.md](docs/beyond-the-demo.md)，等第一次跑通再看。

## 启动顺序

接到任务后，**先读完再动手**，按这次序：

1. [README.md](README.md) — 人类操作入口与完成标准
2. 本文件 — Agent 工作契约
3. [CONVENTIONS.md](CONVENTIONS.md) — 制作红线
4. [tools/tts/README.md](tools/tts/README.md) 与 [tools/video/README.md](tools/video/README.md) — 命令与门禁
5. [examples/top-ranking-demo/README.md](examples/top-ranking-demo/README.md) — 教学示例目录与命令

制作下一期盘点时再读 [docs/runbook.md](docs/runbook.md)。不要跳过启动阅读直接改简报或发明新流程。

## 硬性规则

- **成片渲染与真配音以 Mac 为主。** Chrome 渲染、Qwen3-TTS / MLX 需要 Apple Silicon。Linux / CI 只保证结构门禁与 `smoke-e2e --structure-only`。没有 Chrome 或 Qwen 时停该步，用中文写出下一步；结构门禁可以继续。
- **Cookie 永不提交。** 仓库根目录 `all_cookies.txt`（权限 `0600`）是用户自备输入。不要写入 git、不要打印 Cookie 值、不要改写该文件。工具从不写这个路径。仓库里的 `examples/cookies/` 只有假格式。
- **下载只走 `tools/video/yt_dlp_readonly.py`。** 它把 jar 拷到仓库外的临时快照，避免 yt-dlp 改写规范文件。禁止直接执行 `yt-dlp --cookies all_cookies.txt`。
- **HyperFrames 锁定 `0.6.69`。** 只用 `npx --yes hyperframes@0.6.69 ...`。渲染加 `--sdr`。不要用 `@latest` 或未钉版本。字体离线，不要拉 Google Fonts。
- **禁止静默回退到 Kokoro。** Qwen 权重、参考音或 Apple Silicon 缺失时，该步失败并打印中文下一步。不要改用其他 TTS 引擎凑过门禁。
- **版权素材与密钥不进 git。** 不要提交下载、成片、普通 WAV/MP4、运行时 Cookie、`.env`、百度 token、模型权重，或操作者不打算公开的配音母带。教学画面用本机生成的合法占位竖屏，不要下载 `SOURCES.md` 里的 `example.com`，也不要把版权 MV 放进仓库。

## 目标闭环

默认闭环（教学示例已带简报、选声、清单与文案，不要无故重写）：

```text
简报 BRIEF.md
  → 取材 SOURCES.md / 占位竖屏或合法 URL
  → 配音 voice-selection.json + sidecar（可选真 WAV）
  → 写作契约 project-manifest.json（schema v2）后合成
  → 四道门禁
  → renders/<slug>.mp4 + publishing/xiaohongshu.md
```

接到视频任务时按下列步骤。某一步缺用户自备文件就停这一步，不要整条任务一起扔。

1. 读完启动顺序中的文档。教学示例对照 `examples/top-ranking-demo/README.md`。
2. 跑 `python3 tools/tts/doctor.py`。配音齐备之前，结构模式 `VOICE GATE: PASS mode=structure` 可以接受。真 WAV 先 `python3 tools/tts/setup_check.py`，再 `python3 tools/cli.py smoke-narrate`。缺权重就停配音这一步。
3. 根据原始简报解析**一份** `voice-selection.json`。简报没改就不要重跑；教学示例已经有选择。不要按艺人性别选配音性别。
4. 真下载之前，仓库根目录必须有真实 Netscape jar：`all_cookies.txt`（`0600`）。先跑 `bash tools/video/install_cookies.sh`（只拷格式模板），由人类用筛选过的浏览器导出替换占位值，再跑 `python3 tools/video/check_yt_cookie.py`。缺 Cookie → 停下载；公开样本连通性验证见 `examples/smoke-download/`。只验结构的门禁可以继续。
5. 写 `master.wav` / HTML **之前**，先填好 `project-manifest.json`（schema v2）。
6. `python3 tools/video/verify_project.py` 必须打印 `PROJECT CONTRACT: PASS`。
7. 教学示例成片走 `python3 tools/cli.py smoke-e2e`（占位竖屏 + `hyperframes@0.6.69 --sdr` → mux）。没有旁白 WAV 就铺静音床或轻正弦（加 `--tone`）。没有 Chrome 就停渲染、打印中文下一步。结构门禁：`python3 tools/cli.py smoke-e2e -- --structure-only`。
8. mux 之后确认 `publishing/xiaohongshu.md`，再跑 `python3 tools/video/verify_publishing.py`。
9. 跑 `python3 tools/video/prepare_final_qa.py`。v1 只写待审骨架；不要声称已经做完机器画面 / ASR 审核，也不要伪造人工复核。

四道门禁成功字面（工具原文为英文，须一致）：

```text
VOICE GATE: PASS mode=structure
PROJECT CONTRACT: PASS mode=structure
PUBLISHING COPY: PASS
FINAL VIDEO QA: PASS skeleton pending_machine_qa
```

有真 WAV 后再加 `--require-wav`，期望 `VOICE GATE: PASS mode=wav`。

## 榜单揭晓顺序

`project_kind=top_ranking` 按**名次从低到高**揭晓：末位先播，首位最后。该顺序用于脚本、时间线与 QA。封面与 intro 不列完整歌单、不展示排序、不泄露第一名。封面素材用最先播放的那首（最后一名），并直接接到该名次揭晓。

画面与对外文案不要写 `05→01`、`N→1` 或「倒数开始」。JSON 内部字段可以使用 `playback_order: "N→1"`，仅供脚本与门禁使用。封面标题已经用了中文极致词（「最难 / 最燃 / 被低估」），就不要再盖一个 `TOP N` 角标。

## 向人类回报

每次告一段落时，用中文清楚写出：

- **已读文件**：启动顺序里实际打开过的文档。
- **已执行命令**与关键输出（尤其是四道门禁的字面 PASS / FAIL）。
- **产物路径**：例如 `examples/top-ranking-demo/renders/top-ranking-demo.mp4`、`publishing/xiaohongshu.md`。没有成片就写明停在哪一步。
- **本机缺口**：缺 Cookie、缺合法素材 URL、缺 Qwen 权重、缺自录参考 WAV、缺 Chrome / Mac、缺 Node 22 等。每一项只写人类需要补什么，不要假装已经齐备。
- **诚实边界**：结构 PASS 不等于可发布成片；静音床 / 色条占位只验证闭环；FINAL 骨架不证明画面或 ASR。不要发明 `reviewer_kind=human`。

不要把 Cookie 值、token、参考音频内容或版权媒体写进回复或提交。

## 失败恢复

某一步失败就停这一步。诊断 → 修上游 → 重跑**受影响的**门禁。不要放松机械红线，不要用另一种引擎或假文件凑过。

只在这些情况暂停并回报人类：

- 操作者要求先预览
- 缺用户自备文件（真实 Cookie、有权使用的素材、Qwen 权重、参考 WAV）
- 安全替代方案已经用尽
- 继续会改核心简报（歌单、名次、版本、平台排除、硬时长）

## 目录

- `tools/tts/` — 体检、选声、配音、校验
- `tools/video/` — Cookie、yt-dlp 封装、vfill、门禁、倒数计划、占位片段 / 下载连通性验证
- `examples/top-ranking-demo/` — TOP 教学示例（默认可复现成片路径）
- `examples/narrative-eras-demo/` — 编年 / 叙事脚手架（结构门禁；不成片）
- `examples/cookies/` — Netscape 格式模板（只有假值）
- `examples/smoke-download/` — 公开 YouTube 下载连通性验证
- `docs/` — 第一次跑通之后的次要材料
- `tools/delivery/baidu/` — 可选上传；不属于第一次跑通

## 资源

用 `tools/video/resource_budget.py`。任务之间没有全局锁。环境变量覆盖是 `AMRH_ASR_THREADS`、`AMRH_FFMPEG_THREADS`、`AMRH_HYPERFRAMES_WORKERS`（只能 1–4）。
