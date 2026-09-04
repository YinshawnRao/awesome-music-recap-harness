# 教学示例之后

请先读根目录 README 和 TOP 榜示例。这里没有任何第一次跑通的必做项。

## 其他节目形态

写作契约（`project_kind`）还接受：

| 取值 | 含义 | 参照 |
| --- | --- | --- |
| `top_ranking` | 默认可复现路径。榜单按名次从低到高揭晓（末位先播，首位最后），封面 / intro 保悬念。 | [`examples/top-ranking-demo/`](../examples/top-ranking-demo/) |
| `narrative` | 时间线 / 散文顺序。条目没有 `rank`。 | [`examples/narrative-eras-demo/`](../examples/narrative-eras-demo/) |
| `free_exploration` | 实验；需要非空的 `rationale`。 | 先完成上面两种，再自行写 `rationale` |

配音、取材、发布、mux 规则相同。未走完榜单教学示例之前，不要另开新形态。编年脚手架只锁结构门禁，**没有** HyperFrames 合成；成片仍走 TOP 的 `smoke-e2e`。

## 硬素材门禁

默认是结构模式，这样教学示例不附带片段也能跑。P1 可用
`python3 tools/video/make_placeholder_clips.py` 生成本地合法占位竖屏；那不是版权 MV，也不能代替 `--require-media` 要的真 WAV。

VOICE 两种模式：

- 结构：`verify_voice_usage.py` → `VOICE GATE: PASS mode=structure`（只要 sidecar）
- 真 WAV：加 `--require-wav` → `PASS mode=wav`。P2 用 `smoke-narrate` 写出文件后再开这个开关。

```bash
python3 tools/video/verify_project.py --project examples/top-ranking-demo --require-media
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo --require-wav
```

在真实 WAV / 片段齐备之前，这两个开关会失败。缺 Qwen 权重时不要改用 Kokoro。

## 可选：百度网盘上传

`tools/delivery/baidu/` 是**可选**插件。工作台本体不依赖它。只上传，凭证在仓库外。发现命令：

```bash
python3 tools/cli.py baidu-upload --help
python3 tools/cli.py baidu-upload -- --dry-run \
  --local README.md --remote /apps/amrh/readme.md
```

token 永远不要进 git。见 [tools/delivery/baidu/README.md](../tools/delivery/baidu/README.md)。

## 命令附录

vfill、B 站搜索、资源预算、Cookie 筛选的完整命令在
[tools/video/README.md](../tools/video/README.md) 和
[tools/tts/README.md](../tools/tts/README.md)。用到某个工具之前，优先按教学示例操作。
