# -*- coding: utf-8 -*-
"""AI 编程初体验：最小命令行程序。

任务 5（AI 初体验）要求：使用 AI 编程工具编写一个最小的程序，
完整体验「描述需求 → AI 生成代码 → 本地运行验证 → 微调」的流程。

第一版需求（提示词）：写一个输出“Hello, AI 编程！”的命令行小程序。
第二版需求（微调）：支持通过命令行参数传入姓名，并打印运行时间。

运行示例：
    python hello_ai.py
    python hello_ai.py --name 张三
"""
from __future__ import annotations

import argparse
from datetime import datetime


def build_greeting(name: str | None = None) -> str:
    """构造问候语。name 为空时使用默认问候。"""
    if name:
        return f"Hello, {name}！欢迎使用 AI 编程。"
    return "Hello, AI 编程！"


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 编程初体验最小程序")
    parser.add_argument("--name", default=None, help="要问候的姓名（可选）")
    args = parser.parse_args()

    print(build_greeting(args.name))
    print("运行时间：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
