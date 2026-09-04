# 教学项目之后

先读根目录 README 和 TOP 榜示例。这里没有任何第一次跑通的必做项。

## 其他节目形态

写作契约（`project_kind`）还接受：

| 取值 | 含义 |
| --- | --- |
| `top_ranking` | 旗舰。N→1 倒数揭晓，封面 / intro 保悬念。 |
| `narrative` | 时间线 / 散文顺序。条目没有 `rank`。 |
| `free_exploration` | 实验；需要非空的 `rationale`。 |

配音、取材、发布、mux 规则相同。没走完榜单教学项目之前，不要另开新形态。

## 硬素材门禁

默认是结构模式，这样教学项目不附带片段也能跑。P1 可用
`python3 tools/video/make_placeholder_clips.py` 生成本地合法占位竖屏；那不是版权 MV，也不能代替 `--require-media` 要的真 WAV。

```bash
python3 tools/video/verify_project.py --project examples/top-ranking-demo --require-media
python3 tools/tts/verify_voice_usage.py \
  --selection examples/top-ranking-demo/voice-selection.json \
  --project-root examples/top-ranking-demo --require-wav
```

在真实 WAV / 片段齐备之前，这两个开关会失败。

## 可选：百度网盘上传

`tools/delivery/baidu/` 是**可选**插件。工作台本体不依赖它。token 永远不要进 git。见
[tools/delivery/baidu/README.md](../tools/delivery/baidu/README.md)。

## 命令附录

vfill、B 站搜索、资源预算、Cookie 筛选的完整命令在
[tools/video/README.md](../tools/video/README.md) 和
[tools/tts/README.md](../tools/tts/README.md)。用得到某个工具之前，优先跟教学项目走。
