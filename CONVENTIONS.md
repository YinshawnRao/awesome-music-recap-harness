# CONVENTIONS.md — 可复用的制作红线

请从 [README.md](README.md) 开始。本文件是红线清单，不是「第一次跑通」指南。工具 README 里有额外命令。本地 AI Agent 的工作契约是 [`AGENTS.md`](AGENTS.md)。不要另起一套互相冲突的规则。

## Git 边界

可以提交：源码、文档、schema、选题简报、轻量 QA JSON，以及**假的** Netscape 模板 `examples/cookies/all_cookies.example.txt`。不要提交：下载、成片、普通 WAV/MP4、运行时 Cookie、token、模型权重。根目录 `all_cookies.txt` 是用户自备输入（`0600`），不是 git 资产。`.gitignore` 忽略 `*cookies*.txt`，再把示例文件加回白名单。

## 盘点形态

盘点不只等于 TOP 榜。必须显式写 `project_kind`：

- `top_ranking` — 榜单倒数揭晓：按名次从低到高播放（末位先播，首位最后），封面 / intro 保悬念。
- `narrative` — 时间线或散文顺序；条目没有 `rank`。脚手架：`examples/narrative-eras-demo/`。
- `free_exploration` — 实验；`rationale` 不能为空。

新项目用写作 **schema v2**。

## 双平台取材

除非简报指定某一条 URL 为必用，否则 YouTube **和** B 站都要搜。先锁定版本身份（翻唱 vs 原唱），再官方 MV，再干净度、立体声、分辨率。把选择写进 `SOURCES.md` 和 `project-manifest.json`。`example.com` 占位 URL 只给教学清单用。P1 教学画面用 `make_placeholder_clips.py` 本机生成，不要下载 `example.com`。

## TOP 榜（默认可复现形态）

- 播放顺序按名次从低到高（末位先播，首位最后）。该顺序用于脚本、时间线与 QA；JSON 内部字段可为 `playback_order: "N→1"`。
- 封面和 intro 不列完整歌单、不展示排序、不泄露第一名。
- 画面上不要写 `05→01` / `N→1` / 「倒数开始」。这些记号只出现在内部数据与门禁报错里，不作为对外文案。
- 封面标题已经用了中文极致词（「最难 / 最燃 / 被低估」），就不要再盖一个 `TOP N` 角标。
- 封面素材用**最先播放**的那首（最后一名），并直接接到该名次揭晓。

## 旁白

- 结构：开头 + 每条短转场 + 作品 outro + 固定 CTA。
- intro 里不能出现「接下来」。
- TOP 转场：一次揭晓 + 一个判断；目标 4–6 秒，WAV 硬上限 8 秒。
- 叙事转场：一个节点 + 一层意思；目标 6–8 秒，WAV 硬上限 10 秒。
- 固定 CTA 是 `tools/video/outro_cta.py::FIXED_OUTRO_CTA`，必须是最后一句口播。简报不能替换它。
- 每个项目一份 `voice-selection.json`。不要按艺人性别选配音性别。
- Qwen 缺失 → TTS 这一步失败。不要悄悄改用 Kokoro。
- 纯中文不改写。ASCII 专名可以规范化（`BEYOND → Beyond`，`BTS → B T S`）。

## 画面

- 默认画幅 1080×1920 @ 30fps。
- 用 `vfill.sh` 加黑边，裁切带必须**铺满宽度**。
- 除非简报要求，不加自定义旁白字幕。
- 成片画面上不要水印、URL、提示词、文件路径。
- 字体：项目本地、有授权的 WOFF2。渲染时不要拉 Google Fonts。

## 音频

- 旁白底下压低音乐（大约 25%，300ms）。
- 先预混 `master.wav`，HyperFrames 之后再 mux（HF 会压动态）。
- 真成片上 `>1.5s` 静音是硬失败。不要铺底噪来混过门禁。

## HyperFrames

锁 **0.6.69**。渲染加 `--sdr`。工人数走 `tools/video/resource_budget.py`（`4 → 3 → 2`，环境变量 `AMRH_*` 只能 1–4）。

## 发布

mux 之后、FINAL 之前写 `publishing/xiaohongshu.md`。标题候选 1–5 条（默认 3），正文去空格后 420–900 字，要有一个真问题，8–10 个话题标签，不要 emoji，不要歌名。

## 可选：百度网盘

`tools/delivery/baidu/` 只负责上传，读 `AMRH_BAIDU_*` 或仓库外的密钥文件。发现命令：`python3 tools/cli.py baidu-upload --help`。git 里不能有 token。
