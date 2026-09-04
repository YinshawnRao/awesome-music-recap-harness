# Cookie 示例文件

最短安装路径在根目录 [README](../../README.md)。本页是更长的导出 / 封装说明。

`all_cookies.example.txt` 是一份**合法的 Netscape Cookie 文件**，值全是一眼能看出来的 `PLACEHOLDER_NOT_A_SESSION_*`。它不能当登录态。文件里的注释标出了 YouTube/Google 和 B 站两组字段。

完整的双平台 yt-dlp 流程**必须**有用户自己导出的真实 jar，装到仓库根目录 `all_cookies.txt`（权限 `0600`）。这份运行时文件已被 gitignore。永远不要提交它。只验结构的教学门禁没有 jar 也能跑。

## 安装

```bash
cp examples/cookies/all_cookies.example.txt all_cookies.txt
chmod 0600 all_cookies.txt
```

然后要么就地替换每一个 `PLACEHOLDER_*`，要么用**仓库外**筛出来的候选文件整份覆盖：

```bash
# 原始导出和候选文件都必须在仓库外
python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
  --output /absolute/outside/candidate.txt
cp /absolute/outside/candidate.txt all_cookies.txt
chmod 0600 all_cookies.txt
python3 tools/video/check_yt_cookie.py
```

`check_yt_cookie.py` 从不打印 Cookie 值。仓库里的示例会**故意失败**（`placeholder-value advisory`），直到这些占位符被换掉。缺 `all_cookies.txt` 也是失败：下载不会退回匿名公开路径。

## 从浏览器导出

1. 同一浏览器配置里同时登录 YouTube/Google 和 B 站。
2. 用 Netscape `cookies.txt` 导出插件（例如 “Get cookies.txt LOCALLY”）。文件存到本仓库外面，立刻 `chmod 0600`。
3. 必有字段名写在示例文件注释和 `docs/mac-setup.md`。
4. 本工作台不要给 yt-dlp 喂 `--cookies-from-browser`。

## 唯一允许的 yt-dlp 入口

```bash
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

封装会把 `all_cookies.txt` 拷到**仓库外**的私有 `amrh-cookie-*` 目录，这样 yt-dlp 改不了规范文件。永远不要直接跑 `yt-dlp --cookies all_cookies.txt`。
