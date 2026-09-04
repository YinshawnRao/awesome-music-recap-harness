# 自己做下一期盘点

先跑完 [TOP 教学项目](../examples/top-ranking-demo/) 和根目录 README 的第一次跑通命令，再看这篇。抄那个目录的形状，不要把 `tools/` 里每条脚本都搬过来。

## 1. 按教学项目抄目录

```text
BRIEF.md
SOURCES.md
songs.json                 # 播放顺序 N→1
project-manifest.json      # schema v2
voice-selection.json
narration-request.json
publishing/xiaohongshu.md
package.json               # hyperframes@0.6.69
```

封面 / intro 不要出现完整歌单，也不要泄露 `#1`。

## 2. 先 Cookie，再取材

真下载之前，仓库根目录必须有真实 Netscape jar：`all_cookies.txt`（`0600`）。`python3 tools/video/check_yt_cookie.py` 必须 PASS。

YouTube **和** B 站都要搜。先锁定版本身份，再官方 MV，再干净度。把选择写进 `SOURCES.md` 和清单。下载只走 `tools/video/yt_dlp_readonly.py`。

## 3. 配音，再过项目门禁

整期只用一个声音。TTS 体检变绿之前，空跑旁白就够。写 `master.wav` 或成片 HTML **之前**，`verify_project.py` 必须打印 `PROJECT CONTRACT: PASS`。

```bash
python3 tools/video/countdown_build.py --project <project> --plan-only
```

## 4. 画面、渲染、mux

用 `tools/video/vfill.sh` 加黑边（裁切带铺满宽度）。渲染用 **hyperframes@0.6.69** `--sdr`。把预混好的 `master.wav` 盖到画面上（HyperFrames 会压动态）：

```bash
ffmpeg -i renders/full.mp4 -i master.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest renders/<slug>.mp4
```

## 5. 发布文案 + FINAL

```bash
python3 tools/video/verify_publishing.py --project <project>
python3 tools/video/prepare_final_qa.py --project <project>
```

v1 的 FINAL 只写待审骨架。不要声称已经做完机器画面 / ASR 审核，也不要伪造 `reviewer_kind=human`。

其他形态、百度网盘、`--require-media`：[beyond-the-demo.md](beyond-the-demo.md)。
