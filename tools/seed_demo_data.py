# -*- coding: utf-8 -*-
"""生成演示数据，便于截图 / 演示签到记录页。

说明：这是**测试数据**，仅用于本地演示与截图，
      不会提交到仓库（data/ 已在 .gitignore 中忽略）。

用法：
    python tools/seed_demo_data.py            # 清空后写入演示数据
    python tools/seed_demo_data.py --append    # 追加不清空
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, "data", "signin.db")

# (学号, 姓名, 签到时间 HH:MM, 签退时间 HH:MM 或 None)
# 注意：故意不包含本人（方天恒 / 302023572037），
#       本人的签到记录在演示时通过网页界面真实操作产生。
DEMO = [
    ("302023572001", "陈晓东", "08:31", "11:30"),
    ("302023572018", "林嘉怡", "08:55", "11:32"),
    ("302023572026", "王志远", "09:12", "11:40"),
    ("302023572044", "赵梦琪", "08:47", None),
    ("302023572053", "黄浩然", "09:26", None),
    ("302023572061", "吴思远", "08:38", "11:31"),
]

DATE = "2026-09-29"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--append", action="store_true", help="追加而不是清空当天数据")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if not args.append:
        conn.execute("DELETE FROM records WHERE sign_date = ?", (DATE,))

    inserted = 0
    for no, name, t_in, t_out in DEMO:
        exists = conn.execute(
            "SELECT 1 FROM records WHERE student_no = ? AND sign_date = ?", (no, DATE)
        ).fetchone()
        if exists:
            continue
        status = "已签退" if t_out else "已签到"
        conn.execute(
            "INSERT INTO records (student_no, name, sign_date, sign_in_at, sign_out_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (no, name, DATE, f"{DATE} {t_in}:00",
             f"{DATE} {t_out}:00" if t_out else None, status),
        )
        inserted += 1

    conn.commit()
    total = conn.execute(
        "SELECT COUNT(*) c FROM records WHERE sign_date = ?", (DATE,)
    ).fetchone()["c"]
    conn.close()
    print(f"演示数据写入完成：新增 {inserted} 条，{DATE} 共 {total} 条。")


if __name__ == "__main__":
    main()
