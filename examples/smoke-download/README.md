# 公开 YouTube 下载连通性验证

验证 Cookie 与 `yt_dlp_readonly.py` 这条路径能从网上取回一个文件（冒烟测试）。命令名仍是 `smoke-download`。

## 为什么是 Me at the zoo（`jNQXAC9IVRw`）

[Jawed Karim《Me at the zoo》](https://www.youtube.com/watch?v=jNQXAC9IVRw) 是 YouTube **第一条公开上传**（2005-04-23），大约 19 秒，不是音乐 MV，也不是版权歌单。yt-dlp 和各类下载工具常用它作为合法公开样本。本步骤只证明封装能运行，不把它当作盘点素材。

## 一条命令（仓库根目录）

```bash
python3 tools/cli.py smoke-download
# 或
bash examples/smoke-download/run.sh
```

输出写到本目录 `out/`（gitignore，不提交）。

## Cookie

本仓库**只允许** `python3 tools/video/yt_dlp_readonly.py` 调用 yt-dlp。封装必须读仓库根目录 `all_cookies.txt`。

| 情况 | 行为 |
| --- | --- |
| 没有 jar | **失败**，打印 `bash tools/video/install_cookies.sh` |
| 还是 `PLACEHOLDER_*` | 打印清楚警告；**仍会尝试**这条公开视频 |
| 真实导出 | 正常走封装下载 |

部分网络可以**不登录**就下载这条公开 YouTube。成功只说明公开样本能取流，**不等于** B 站或完整教学下载能运行。B 站 / 完整示例 **必须**换成真实 Netscape 导出，再跑 `python3 tools/video/check_yt_cookie.py`。

不要自行执行 `yt-dlp --cookies all_cookies.txt`。
