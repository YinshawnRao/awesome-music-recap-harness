# 公开 YouTube 下载烟雾

证明 Cookie + `yt_dlp_readonly.py` 这条路径能从网上取回一个文件。

## 为什么是 Me at the zoo（`jNQXAC9IVRw`）

[Jawed Karim《Me at the zoo》](https://www.youtube.com/watch?v=jNQXAC9IVRw) 是 YouTube **第一条公开上传**（2005-04-23），大约 19 秒，不是音乐 MV，也不是版权歌单。yt-dlp 和各种下载工具常用它当合法公开样本。本烟雾只为证明封装能跑，不把它当盘点素材。

## 一条命令（仓库根目录）

```bash
python3 tools/cli.py smoke-download
# 或
bash examples/smoke-download/run.sh
```

输出写到本目录 `out/`（gitignore，不提交）。

## Cookie

本仓库**只允许** `python3 tools/video/yt_dlp_readonly.py` 调 yt-dlp。封装必须读仓库根目录 `all_cookies.txt`。

| 情况 | 烟雾会怎样 |
| --- | --- |
| 没有 jar | **失败**，打印 `bash tools/video/install_cookies.sh` |
| 还是 `PLACEHOLDER_*` | 打印清楚警告；**仍会尝试**这条公开视频 |
| 真实导出 | 正常走封装下载 |

部分网络可以**不登录**就下这条公开 YouTube。成功只说明公开样本能取流，**不等于** B 站或完整教学下载能跑。B 站 / 完整 demo **必须**换成真实 Netscape 导出，再跑 `python3 tools/video/check_yt_cookie.py`。

永远不要自己跑 `yt-dlp --cookies all_cookies.txt`。
