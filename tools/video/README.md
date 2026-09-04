# tools/video — 命令附录

请从根目录 [README](../../README.md) 和
[examples/top-ranking-demo/](../../examples/top-ranking-demo/) 开始。本地 AI Agent 请同时遵守 [AGENTS.md](../../AGENTS.md)。本页列额外命令。第一次跑通用不到其中大部分。

## 命令

```bash
# Cookie 安装 + 公开下载连通性验证 + 教学占位竖屏
bash tools/video/install_cookies.sh
python3 tools/cli.py smoke-download
python3 tools/video/make_placeholder_clips.py

# 配音试生成（缺权重会失败并打印中文下一步）
python3 tools/tts/setup_check.py
python3 tools/cli.py smoke-narrate

# 成片连通性验证（无 Chrome 会失败并打印中文下一步）
python3 tools/cli.py smoke-e2e
python3 tools/cli.py smoke-e2e -- --structure-only
python3 tools/cli.py mix-master -- --tone

# 可选：百度网盘（凭证在仓库外；空跑不要 token）
python3 tools/cli.py baidu-upload --help
python3 tools/cli.py baidu-upload -- --dry-run \
  --local README.md --remote /apps/amrh/readme.md

# 安全下载（必须有 jar；唯一允许的 yt-dlp 入口）
python3 tools/video/check_yt_cookie.py
python3 tools/video/yt_dlp_readonly.py -- "<URL>" --skip-download --print id,title

# 双平台搜索
python3 tools/video/bili_search.py "PLACEHOLDER artist official MV" 5

# 加黑边到 1080×1920（裁切带铺满宽度）
bash tools/video/vfill.sh raw.mp4 clips/vert_item.mp4 1920:800:0:140

# 门禁
python3 tools/video/verify_project.py --project examples/top-ranking-demo
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
python3 tools/video/prepare_final_qa.py --project examples/top-ranking-demo

# 榜单倒数规划器
python3 tools/video/countdown_build.py --project examples/top-ranking-demo --plan-only

# 自适应 HyperFrames 工人数（在项目目录里跑）
python3 ../../tools/video/resource_budget.py hyperframes -- \
  npx --yes hyperframes@0.6.69 render --output renders/full.mp4 --sdr
```

## 四道门禁（顺序固定）

1. **VOICE** — `tools/tts/verify_voice_usage.py`
2. **PROJECT** — `verify_project.py`（写 master.wav / HTML 之前）
3. **PUBLISHING** — mux 之后、FINAL 之前跑 `verify_publishing.py`
4. **FINAL** — `prepare_final_qa.py`（v1 只写待审骨架）

`--require-media` / `--require-wav` 会把结构 PASS 升级成硬素材门禁。

## master.wav 混流

HyperFrames 会归一化音频并压掉闪避。一定要把预混好的 `master.wav` 盖到画面上：

```bash
ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest renders/<slug>.mp4
```

## Cookie（完整流水线必做）

双平台下载流程**必须**有仓库根目录的 Netscape jar：`all_cookies.txt`（权限 `0600`）。只验结构的门禁没有它也能跑。缺 jar 或还是占位符时，`yt_dlp_readonly.py` 和 `check_yt_cookie.py` 会硬停。

1. 拷仓库里的格式模板，或用筛选过的导出整份覆盖：

   ```bash
   bash tools/video/install_cookies.sh
   ```

2. 从浏览器导出真实 Netscape 文件（YouTube/Google + B 站）。
   推荐 Chrome 扩展 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)。
   筛选必须在**仓库外**（`filter_cookie_jar.py` 拒绝仓库内路径）。
   你自己把候选文件拷到 `all_cookies.txt`。工具从不写这个路径。

3. 校验：

   ```bash
   python3 tools/video/check_yt_cookie.py
   ```

   检查从不打印 Cookie 值。示例文件在还留着 `PLACEHOLDER_*` 时会故意失败。

4. 下载**只**走 `yt_dlp_readonly.py`。它会把 jar 拷到仓库外的私有
   `amrh-cookie-*` 目录，避免 yt-dlp 改写规范文件。不要跑 `yt-dlp --cookies all_cookies.txt`。

见 [examples/cookies/README.md](../../examples/cookies/README.md)。其他节目形态和百度网盘：[docs/beyond-the-demo.md](../../docs/beyond-the-demo.md)。编年脚手架：[examples/narrative-eras-demo/](../../examples/narrative-eras-demo/)。小红书文案：[docs/publishing.md](../../docs/publishing.md)。CI 对照：[docs/ci.md](../../docs/ci.md)。
