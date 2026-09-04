# Mac 安装（附录）

最短可复制路径在根目录 [README](../README.md)。本页补 TTS 细节和更完整的 Cookie 表。v1 **以 Mac 为主**。

## 必装

```bash
brew install ffmpeg yt-dlp
# Node 22+（Homebrew node、fnm 或 nvm 均可）
node -v   # >= 22
python3 --version
```

HyperFrames：

```bash
npx --yes hyperframes@0.6.69 doctor
```

必须带版本钉 `0.6.69`。不要用 `@latest`。

## Cookie（完整下载流水线必做）

双平台 YouTube + B 站的 yt-dlp 流程**必须**有 Netscape Cookie 文件。只验结构的教学门禁没有它也能过。不要把 Cookie 当成可有可无的锦上添花。

仓库里的 `examples/cookies/all_cookies.example.txt` **只保证格式**：合法 Netscape 表头和列，值全是假的 `PLACEHOLDER_NOT_A_SESSION_*`。它不能登录任何人。根目录 `all_cookies.txt` 已被 gitignore。

### 从浏览器导出

用能写出 **Netscape HTTP Cookie File**（制表符分隔的 `cookies.txt`）的插件。常见名字：「Get cookies.txt LOCALLY」「cookies.txt」。导出时，同一配置里要同时登录 YouTube/Google **和** B 站。原始文件**先存到本仓库外面**（例如 `~/Downloads/raw-cookies.txt`），立刻 `chmod 0600`。

两组字段都要有：

| 平台 | 必有字段名 | 常见域名 |
| --- | --- | --- |
| YouTube / Google | `LOGIN_INFO`、`SID`、`HSID`、`SSID`、`SAPISID`、`APISID`、`__Secure-3PSID` | `.youtube.com`、`.google.com` |
| B 站 | `SESSDATA`、`bili_jct`、`DedeUserID` | `.bilibili.com` |

本工作台**不要**走 `--cookies-from-browser`。规范 jar 的唯一允许 yt-dlp 入口是只读封装。

### 安装路径

```bash
# 1）从仓库里的格式模板起步（可选，但建议）
cp examples/cookies/all_cookies.example.txt all_cookies.txt

# 2）在仓库外筛选真实浏览器导出（源文件和输出都必须在仓库外）
python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
  --output /absolute/outside/candidate.txt

# 3）你自己把候选文件拷到运行时路径。工具从不写这个路径。
cp /absolute/outside/candidate.txt all_cookies.txt
chmod 0600 all_cookies.txt

# 4）静态预检（不打印值；留下 PLACEHOLDER_* 就会失败）
python3 tools/video/check_yt_cookie.py

# 5）唯一允许的 yt-dlp 入口 — 把 jar 快照到仓库外
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

`yt_dlp_readonly.py` 会把 `all_cookies.txt` 拷到系统临时目录下的私有 `amrh-cookie-*` 文件夹，这样 yt-dlp 退出时改不了规范文件。永远不要直接跑 `yt-dlp --cookies all_cookies.txt`。

## 可选：Qwen / MLX TTS

Apple Silicon 上：

1. 单独建一个解释器（不要和通用 Whisper 虚拟环境混用）。
2. 安装合法的 `mlx-audio==0.4.5`，以及 `tools/tts/config.json` 里写明的 Qwen3-TTS 0.6B Base 8-bit 模型树。
3. 导出：

```bash
export AMRH_QWEN_PYTHON=/path/to/qwen.venv/bin/python
export AMRH_QWEN_BASE_MODEL=/path/to/Qwen3-TTS-12Hz-0.6B-Base-8bit@REVISION
```

4. 把你自己有授权的 `reference.wav` 放到 `tools/tts/voices/CVxxx-*/`。
5. `python3 tools/tts/doctor.py --voice CV007 --require-reference`

`metal_preflight.py` 会在导入 MLX **之前**检查 Metal。没有 Metal，当前 TTS 步骤直接失败。不要悄悄改用 Kokoro。

## Linux / Kokoro

只作为将来的显式旧引擎提起（`hexgrad/Kokoro-82M`）。v1 用这套工作台不需要它。

## 不带素材的测试

```bash
python3 -m pytest
```
