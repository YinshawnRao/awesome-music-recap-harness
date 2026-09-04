# 素材

## P1 教学路径（默认）

**不要下载下表的 `example.com`。** 那些 URL 不能取流，也不是版权歌单。

P1 用本机生成的合法占位竖屏（ffmpeg 色条 / 色块，可加短鸣）：

```bash
python3 tools/video/make_placeholder_clips.py
```

写入 `footage/rank-0N.mp4` 和 `clips/vert_rank-0N.mp4`（均 gitignore）。清单里的 `clip` 路径已经对上。换成真实官方 URL 是后面的事，不是 P1。

公开下载连通性验证走另一条路径（YouTube 第一条上传《Me at the zoo》），见 [examples/smoke-download/](../smoke-download/README.md)。那条视频不是本榜歌单。

## 以后换成真实素材

每一条锁定前都必须在 **YouTube 和 B 站** 搜过。下表仍是**带标签的示例占位 URL**，真渲染之前必须换成你自己有权使用的官方源。

| 名次 | 歌名 | 表演者 | YouTube 占位 | B 站占位 | 取舍 |
| --- | --- | --- | --- | --- | --- |
| 5 | 纸灯笼 | 北城 | https://example.com/placeholder/yt-lantern | https://example.com/placeholder/bv-lantern | P1 用本地生成片段；有真实素材后优先官方 MV |
| 4 | 夜渡 | 北城 | https://example.com/placeholder/yt-ferry | https://example.com/placeholder/bv-ferry | 同上 |
| 3 | 玻璃港 | 北城 | https://example.com/placeholder/yt-harbor | https://example.com/placeholder/bv-harbor | 同上 |
| 2 | 北窗 | 北城 | https://example.com/placeholder/yt-window | https://example.com/placeholder/bv-window | 同上 |
| 1 | 末班月台 | 北城 | https://example.com/placeholder/yt-platform | https://example.com/placeholder/bv-platform | 同上 |

回执（URL、时间窗、SHA）在真下载之后写进 `project-manifest.json`。永远不要把 Cookie 或 yt-dlp 的 `info_json` 拷进项目。
