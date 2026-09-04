# 架构

先看根目录 [README](../README.md) 和 [TOP 教学项目](../examples/top-ranking-demo/)。本页讲「为什么」，不是第一次跑通路径。

AMRH 是一套**音乐盘点工作台**。盘点 = 用取材片段 + 旁白 + 合成层搭起来的结构化短视频。榜单只是其中一种形态。

其他 `project_kind` 和可选的百度网盘插件：
[beyond-the-demo.md](beyond-the-demo.md)。

## project_kind

```text
top_ranking  ── 旗舰示例（N→1 倒数揭晓，保悬念）
narrative    ── 时间线 / 散文 / 人物纪录片（按脚本顺序，没有 rank）
free_exploration ── 音乐或画面实验（必须写 rationale）
```

写作契约（`tools/video/project-manifest.schema.json`）是共用的。门禁按 `project_kind` 分支，而不是把单一格式写死进工具。`examples/top-ranking-demo/` 是带名次的参考实现（也是唯一一条 `smoke-e2e` 成片路径）。叙事脚手架在 [`examples/narrative-eras-demo/`](../examples/narrative-eras-demo/)，复用同一套配音、取材、发布规则，只是省略 `rank`，P4 不提交 HyperFrames 合成。

## 分层

1. **取材** — YouTube 和 B 站并行，走 `yt_dlp_readonly.py`
   （仓库根目录 `all_cookies.txt` 的唯一允许 yt-dlp 入口）、
   `bili_search.py`，以及文档里的 `bili_dl.py` 412 回退。完整下载流水线必须有 Netscape jar；封装会把快照放到仓库外，避免 yt-dlp 改写原文件。先版本身份，再官方 MV，再干净度 / 立体声 / 分辨率。
2. **画面** — `vfill.sh` 加黑边（裁切带铺满宽度）。除非用户要求、并且每一帧都看过，否则不要激进竖裁。
3. **配音** — 解析一次（`resolve_voice.py`），用 `narrate.py` 生成，用 `verify_voice_usage.py` 校验。文档路径是 Mac 上的 Qwen/MLX。
4. **计划** — TOP 用 `countdown_build.py`；叙事节目仍要填 schema v2 的旁白角色（开头、每条转场、作品 outro、固定 CTA），除非是已记录的自由探索例外。
5. **合成** — HyperFrames **0.6.69**，`--sdr`，工人数走
   `resource_budget.py`（`4 → 3 → 2`）。
6. **混流** — 预混 `master.wav` 替换 HyperFrames 音频。
7. **发布** — `publishing/xiaohongshu.md`，然后 FINAL 骨架。

## 资源预算

重的 FFmpeg、ASR、HyperFrames 进程会在 `/tmp/amrh-resource-v1-<uid>/` 下挂 PID 标记，立刻在 4、3、2 个工人里选一档。任务之间没有锁、也没有队列。用 `AMRH_FFMPEG_THREADS`、`AMRH_HYPERFRAMES_WORKERS` 或 `AMRH_ASR_THREADS` 覆盖（只能 1–4）。

## 诚实边界

哈希、sidecar、回执只证明**本机一致**。它们不能证明配音来源、官方频道身份，或人工复核。永远不要伪造 `reviewer_kind=human`。
