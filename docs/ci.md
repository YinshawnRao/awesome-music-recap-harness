# CI 和本机分别做什么

先看根目录 [README](../README.md)。本页只对照 **GitHub Actions 会跑什么**，以及 **仍要你自己的 Mac**。

工作流：[`.github/workflows/structure-gates.yml`](../.github/workflows/structure-gates.yml)。推到 `main` 或开 PR 就会跑。

## CI 会跑（不需要 Chrome / Qwen / Cookie）

| 步骤 | 命令 | 证明什么 |
| --- | --- | --- |
| 单元测试 | `python3 -m pytest` | 门禁、Cookie 封装、占位片段、百度计划等 |
| 旗舰结构烟雾 | `python3 tools/cli.py smoke-e2e -- --structure-only` | 合成文件齐、四道门禁 PASS；**不渲染** |
| 叙事脚手架 | `verify_voice_usage` / `verify_project` / `verify_publishing` / `prepare_final_qa` | `examples/narrative-eras-demo/` 契约站得住 |
| 百度空跑 | `python3 tools/cli.py baidu-upload -- --dry-run ...` | 计划能算、不联网、不读 token |

CI 机器会装 `ffmpeg`，方便占位片段测试。它**不会**装 Chrome、不会下 Qwen 权重、不会读 `all_cookies.txt`。

## 仍要本机 Mac

| 你想做的事 | 为什么 CI 不做 |
| --- | --- |
| `python3 tools/cli.py smoke-e2e` 渲出可播放 mp4 | HyperFrames 要 Chrome + Node 22 |
| `python3 tools/cli.py smoke-narrate` 出真 WAV | Qwen / MLX 只要 Apple Silicon + 自备权重 + 自录参考 |
| `python3 tools/cli.py smoke-download` 真拉公开样本 | 部分网络仍要真实 Netscape jar |
| 双平台正式下载 | 必须仓库根目录 `all_cookies.txt`（`0600`），且不能进 git |
| 百度实际上传 | 仓库外的 token；CI 只做 `--dry-run` |

Linux 上跑完整 `smoke-e2e` 时，缺 Chrome 会失败并用中文写出下一步。结构门禁可以继续。
