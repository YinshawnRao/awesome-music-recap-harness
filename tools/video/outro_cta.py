#!/usr/bin/env python3
"""Canonical closing CTA — single source of truth (above a per-show brief).

Change this string only as a global convention change, and update CONVENTIONS.md
plus tests in the same commit.
"""

FIXED_OUTRO_CTA = (
    "你最想为哪一首投票？评论区告诉我。"
    "记得点赞、收藏、关注我，下一期，可能就盘到你单曲循环过的那一首。"
)


if __name__ == "__main__":
    print(FIXED_OUTRO_CTA)
