# 小红书发布文案

mux 之后、FINAL 之前写 `publishing/xiaohongshu.md`，再跑：

```bash
python3 tools/video/verify_publishing.py --project examples/top-ranking-demo
# 或
python3 tools/cli.py publishing-verify -- --project examples/top-ranking-demo
```

成功那一行（工具原文）：`PUBLISHING COPY: PASS`。门禁只验结构，不判断标题传播效果。

## 文件长什么样

```markdown
# 小红书发布文案

## 标题候选（第一条为首选）

- 第一条标题
- 第二条标题
- 第三条标题

## 正文

……成稿正文，最后一行只有话题标签。
```

三个一级 / 二级标题必须原样出现，顺序不能改。标题候选只能是 `- 标题` 这种列表。

## 机械红线

| 规则 | 数字 |
| --- | --- |
| 标题候选 | 1–5 条（教学示例用 3 条） |
| 正文去空格后 | 420–900 字 |
| 互动 | 正文里要有一个真问题（`？` 或 `?`） |
| 话题标签 | 最后一行 8–10 个，彼此不重复 |
| 禁止 | emoji、歌名（清单里的 `title`）、额外 Markdown 标题 |

文案必须提到**至少一位表演者**，或封面主题里的一个非空词（「北城」「被低估」这类）。泛词「盘点 / 音乐 / TOP」不算主题。

教学示例已经有一份能过门禁的文案：[`examples/top-ranking-demo/publishing/xiaohongshu.md`](../examples/top-ranking-demo/publishing/xiaohongshu.md)。编年脚手架另有一份：[`examples/narrative-eras-demo/publishing/xiaohongshu.md`](../examples/narrative-eras-demo/publishing/xiaohongshu.md)。

## 写法建议（不是门禁）

- 封面已经保悬念的榜单：文案也不要提前报第一名、不要列完整歌单。
- 编年 / 叙事：可以说时期，仍然不要把歌名写进标题或正文。
- 固定口播 CTA 是成片最后一句，文案不必重复写出；互动问题要写得具体。
