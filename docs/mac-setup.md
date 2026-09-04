# Mac 安装（附录）

可复现安装步骤见根目录 [README](../README.md)。本页把 **配音**写成可以按序执行的命令。v1 **以 Mac / Apple Silicon 为主**。

仓库**不附带** Qwen 权重、也不附带任何人的参考 WAV。缺了就失败，并打印中文下一步。**不要改用 Kokoro。**

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

双平台 YouTube + B 站的 yt-dlp 流程**必须**有 Netscape Cookie 文件。只验结构的教学门禁没有它也能过。Cookie 是完整下载流水线的硬前置条件，不是可选项。

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
bash tools/video/install_cookies.sh
# 等价于：cp examples/cookies/all_cookies.example.txt all_cookies.txt

# 2）在仓库外筛选真实浏览器导出（源文件和输出都必须在仓库外）
python3 tools/video/filter_cookie_jar.py /absolute/outside/raw.txt \
  --output /absolute/outside/candidate.txt

# 3）将候选文件拷到运行时路径。工具从不写这个路径。
cp /absolute/outside/candidate.txt all_cookies.txt
chmod 0600 all_cookies.txt

# 4）静态预检（不打印值；留下 PLACEHOLDER_* 就会失败）
python3 tools/video/check_yt_cookie.py

# 5）唯一允许的 yt-dlp 入口 — 把 jar 快照到仓库外
python3 tools/video/yt_dlp_readonly.py -- --skip-download --print id "<URL>"
```

`yt_dlp_readonly.py` 会把 `all_cookies.txt` 拷到系统临时目录下的私有 `amrh-cookie-*` 文件夹，这样 yt-dlp 退出时改不了规范文件。永远不要直接跑 `yt-dlp --cookies all_cookies.txt`。

## P2：Apple Silicon 上的 Qwen3-TTS / MLX

只支持 **M 系列 Mac**。Intel Mac、Linux、无 Metal 的远程机会失败。权重不随仓库分发。

### 1. 确认机器

```bash
uname -sm
# 期望：Darwin arm64
python3 tools/tts/metal_preflight.py
# 期望：QWEN METAL PREFLIGHT: PASS
```

不是 `Darwin arm64` 就停。不要改用 Kokoro。

### 2. 建 Qwen 解释器

```bash
bash tools/tts/bootstrap_mac.sh
```

这一步会：

- 再确认一次 Apple Silicon + Metal
- 在 `tools/tts/qwen.venv/` 建独立虚拟环境（不要和 Whisper 混用）
- 安装钉死的 `mlx-audio==0.4.5`
- 写一份 gitignore 的 `tools/tts/runtime/env.sh`

**不会**替你下载模型。

每个新终端：

```bash
source tools/tts/runtime/env.sh
```

等价于：

```bash
export AMRH_QWEN_PYTHON="$PWD/tools/tts/qwen.venv/bin/python"
# AMRH_QWEN_BASE_MODEL 在下一步下载之后再设
```

### 3. 合法下载权重（仓库不附带）

模型卡：[mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit)

钉死 revision（写在 `tools/tts/config.json`）：`50f45ef0047cde7e84c2ef04326acb8ada2436a7`

大约 2GB。请从 Hugging Face 合法取得，不要把权重提交进 git。

```bash
python3 -m pip install -U huggingface_hub
huggingface-cli download mlx-community/Qwen3-TTS-12Hz-0.6B-Base-8bit \
  --revision 50f45ef0047cde7e84c2ef04326acb8ada2436a7 \
  --local-dir "$HOME/amrh-models/Qwen3-TTS-12Hz-0.6B-Base-8bit"

export AMRH_QWEN_BASE_MODEL="$HOME/amrh-models/Qwen3-TTS-12Hz-0.6B-Base-8bit"
# 也可以写进 tools/tts/runtime/env.sh 再 source
```

目录里至少要有 `config.json` 或 `*.safetensors`。空文件夹会失败。

生成时**不会**自动从网上拉模型（`offline_required`）。`AMRH_QWEN_BASE_MODEL` 必须指向本机树。

### 4. 自录约 10 秒 `reference.wav`

教学示例用 **CV007**。详细要点：[tools/tts/voices/local/README.md](../tools/tts/voices/local/README.md)。

- 安静房间，单声道 16-bit PCM WAV
- 目标约 10 秒（8–15 秒）
- 读 registry 里的参考句

```bash
python3 tools/tts/install_reference.py --print-tips
python3 tools/tts/install_reference.py ~/Desktop/reference.wav
# 装到 tools/tts/voices/local/CV007/reference.wav（gitignore）
```

### 5. 体检（失败会写中文下一步）

```bash
python3 tools/tts/setup_check.py
# 或
python3 tools/cli.py tts-setup
```

期望最后一行：`TTS SETUP: PASS`。

缺 Metal、缺 `AMRH_QWEN_*`、缺模型树、缺参考 WAV → 退出码 2，不会悄悄改用 Kokoro。

结构门禁仍然可以只跑：

```bash
python3 tools/tts/doctor.py
# TTS DOCTOR: PASS structure-only   ← 还没有真 WAV，这是正常的
```

真配音再加：

```bash
python3 tools/tts/doctor.py --voice CV007 --require-reference
```

### 6. 生成一句，再可选整批

```bash
python3 tools/cli.py smoke-narrate
# 写出 examples/top-ranking-demo/audio/smoke.wav

python3 tools/cli.py smoke-narrate -- --full
# 再跑教学示例 narration-request.json → narration/*.wav
```

不要加 `--dry-run`。空跑 sidecar 只给第一次结构走查用。

## Linux / Kokoro

只作为将来的显式旧引擎提起（`hexgrad/Kokoro-82M`）。v1 用这套工作台不需要它。缺 Qwen **不要**回退过去。

## 不带素材的测试

```bash
python3 -m pytest
```
