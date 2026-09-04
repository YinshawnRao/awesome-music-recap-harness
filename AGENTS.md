# AGENTS.md

人从 [README.md](README.md) 和
[examples/top-ranking-demo/](examples/top-ranking-demo/) 开始。本文件给贡献者自动化用，不是操作手册。操作者的目标细节不要写进这里。

## 意图

帮另一个人按 README 走完 TOP 榜教学项目。不要一上来铺开所有 `project_kind` 或可选插件。

教学项目是 `examples/top-ranking-demo/`（N→1）。其他形态写在 `docs/beyond-the-demo.md`，等第一次跑通再看。

## 目录

- `tools/tts/` — 体检、选声、配音、校验
- `tools/video/` — Cookie、yt-dlp 封装、vfill、门禁、倒数计划、P1 占位片段 / 烟雾下载
- `examples/top-ranking-demo/` — TOP 教学项目（旗舰可跑通路径）
- `examples/narrative-eras-demo/` — 编年 / 叙事脚手架（结构门禁；不成片）
- `examples/cookies/` — Netscape 格式模板（只有假值）
- `examples/smoke-download/` — 公开 YouTube 下载烟雾
- `docs/` — 第一次跑通之后的次要材料
- `tools/delivery/baidu/` — 可选；不属于第一次跑通

## 接到视频任务时

1. 先读 `README.md` 和 `examples/top-ranking-demo/README.md`。需要红线再读
   `CONVENTIONS.md`。
2. 跑 `python3 tools/tts/doctor.py`（在配音齐备之前，只验结构的 PASS 可以接受）。
   真 WAV 先 `python3 tools/tts/setup_check.py`，再 `python3 tools/cli.py smoke-narrate`。
   缺权重就停这一步，打印中文下一步。不要改用 Kokoro。
3. 根据原始简报解析**一份** `voice-selection.json`。简报没改就不要重跑；教学项目已经有选择。
4. 真下载之前，仓库根目录必须有 Netscape jar：`all_cookies.txt`（`0600`）。
   先跑 `bash tools/video/install_cookies.sh`（只拷格式模板），用筛选过的浏览器导出替换占位值，再跑
   `python3 tools/video/check_yt_cookie.py`。唯一允许的 yt-dlp 入口是
   `yt_dlp_readonly.py`（仓库外的临时快照）。永远不要改写 `all_cookies.txt`。
   缺 Cookie → 停下载这一步；公开烟雾见 `examples/smoke-download/`。只验结构的门禁可以继续。
5. 写 master / HTML **之前**，先填好 `project-manifest.json`（schema v2）。
6. `verify_project.py` 必须打印 `PROJECT CONTRACT: PASS`。
7. 教学项目成片走 `python3 tools/cli.py smoke-e2e`（占位竖屏 + hyperframes@0.6.69 `--sdr` → mux）。没有旁白 WAV 就静音 / 轻正弦床。没有 Chrome 就停渲染、打印中文下一步；结构门禁可以继续。
8. mux 之后写 `publishing/xiaohongshu.md`，再跑 `verify_publishing.py`。
9. 跑 `prepare_final_qa.py`。v1 只写待审骨架；不要声称已经做完机器画面 / ASR 审核，也不要伪造人工复核。

## 恢复

某一步失败就停这一步，不要整条任务一起扔。诊断 → 修上游 → 重跑受影响的门禁。不要放松机械红线。不要发明 `reviewer_kind=human`。

只在这些情况暂停：用户要求预览、缺用户自备文件、安全替代方案已经用尽，或继续会改核心简报（歌单、名次、版本、平台排除、硬时长）。

## 资源

用 `tools/video/resource_budget.py`。任务之间没有全局锁。环境变量覆盖是
`AMRH_ASR_THREADS`、`AMRH_FFMPEG_THREADS`、`AMRH_HYPERFRAMES_WORKERS`（1–4）。

## 密钥

永远不要提交运行时 jar（`all_cookies.txt`）、百度 token、`.env`，或你不打算公开的配音母带。仓库里的 Cookie 示例只有假格式。百度模块是可选的。

## HyperFrames

只用 `npx --yes hyperframes@0.6.69 ...`。渲染加 `--sdr`。字体离线。
