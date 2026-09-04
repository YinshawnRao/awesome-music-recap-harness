# Cookie：最短复制路径

完整双平台下载必须有仓库根目录 `all_cookies.txt`（`0600`）。仓库里的 `all_cookies.example.txt` 是**假的**格式模板（`PLACEHOLDER_NOT_A_SESSION_*`），不能登录。永远不要提交运行时 jar。

```bash
# 1. 拷模板（不覆盖已有的真实 jar）
bash tools/video/install_cookies.sh

# 2. 同一浏览器配置登录 YouTube/Google + B 站，导出 Netscape cookies.txt
#    原始文件先放仓库外，chmod 0600

# 3. 仓库外筛选，再自己覆盖
python3 tools/video/filter_cookie_jar.py "$HOME/Downloads/raw-cookies.txt" \
  --output "$HOME/Downloads/candidate-cookies.txt"
cp "$HOME/Downloads/candidate-cookies.txt" all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

`check_yt_cookie.py` 从不打印 Cookie 值。留下 `PLACEHOLDER_*` 会故意失败。缺 jar 时下载不会开始。

公开 YouTube 样本在部分网络可以不登录就下（见 [烟雾](../smoke-download/README.md)）。**B 站和完整教学下载仍必须换成真实导出。**

本工作台不要给 yt-dlp 喂 `--cookies-from-browser`。唯一入口：

```bash
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

封装把 jar 拷到仓库外的 `amrh-cookie-*`，避免 yt-dlp 改写原文件。
