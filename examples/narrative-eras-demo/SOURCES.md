# 素材

## 脚手架路径（默认）

**不要下载下表的 `example.com`。** 那些 URL 不能取流，也不是版权歌单。

本目录**不**生成占位竖屏，也没有 HyperFrames 合成。P4 只锁写作契约。要看本机色条 → 成片，用 [TOP 教学项目](../top-ranking-demo/SOURCES.md) 的 `make_placeholder_clips.py`。

公开下载烟雾走另一条路径（YouTube 第一条上传《Me at the zoo》），见 [examples/smoke-download/](../smoke-download/README.md)。那条视频不是本编年歌单。

## 以后换成真实素材

每一条锁定前都必须在 **YouTube 和 B 站** 搜过。下表仍是**带标签的示例占位 URL**。

| 时期 | 歌名 | 表演者 | YouTube 占位 | B 站占位 | 取舍 |
| --- | --- | --- | --- | --- | --- |
| 早期 | 旧收音机 | 南港 | https://example.com/placeholder/yt-radio | https://example.com/placeholder/bv-radio | 脚手架锁；有真实素材后优先官方现场 |
| 中段 | 末班路灯 | 南港 | https://example.com/placeholder/yt-lamps | https://example.com/placeholder/bv-lamps | 同上 |
| 江边 | 江面回声 | 南港 | https://example.com/placeholder/yt-echo | https://example.com/placeholder/bv-echo | 同上 |

回执（URL、时间窗、SHA）在真下载之后写进 `project-manifest.json`。永远不要把 Cookie 或 yt-dlp 的 `info_json` 拷进项目。
