# -*- coding: utf-8 -*-
"""数据访问层：封装 SQLite 的建表与读写。

把数据库操作集中在 Store 类里，路由层只调用方法，
便于后续替换存储实现（工程化的分层思路）。
"""
from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_no  TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    sign_date   TEXT    NOT NULL,          -- 签到日期 YYYY-MM-DD
    sign_in_at  TEXT,                      -- 签到时间 YYYY-MM-DD HH:MM:SS
    sign_out_at TEXT,                      -- 签退时间 YYYY-MM-DD HH:MM:SS
    status      TEXT    NOT NULL DEFAULT '已签到',
    UNIQUE (student_no, sign_date)         -- 同一学号同一天只允许一条记录
);
CREATE INDEX IF NOT EXISTS idx_records_date ON records (sign_date);
"""


class Store:
    """签到数据的持久化封装。"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_schema()

    # ------------------------------------------------------------------ 基础
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    # ------------------------------------------------------------------ 写入
    def sign_in(self, student_no: str, name: str) -> tuple[bool, str]:
        """签到。返回 (是否成功, 提示信息)。"""
        today = date.today().isoformat()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._connect() as conn:
            existed = conn.execute(
                "SELECT * FROM records WHERE student_no = ? AND sign_date = ?",
                (student_no, today),
            ).fetchone()

            if existed:
                # 已经把「防重复签到」做成显式校验，而不是只靠数据库约束报错
                return False, f"学号 {student_no} 今天已经签过到了（{existed['sign_in_at']}），请勿重复签到。"

            conn.execute(
                "INSERT INTO records (student_no, name, sign_date, sign_in_at, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (student_no, name, today, now, "已签到"),
            )
        return True, f"{name}（{student_no}）签到成功，时间 {now}。"

    def sign_out(self, student_no: str) -> tuple[bool, str]:
        """签退。返回 (是否成功, 提示信息)。"""
        today = date.today().isoformat()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM records WHERE student_no = ? AND sign_date = ?",
                (student_no, today),
            ).fetchone()

            if row is None:
                return False, f"学号 {student_no} 今天还没有签到记录，无法签退。"
            if row["sign_out_at"]:
                return False, f"学号 {student_no} 今天已经签退过了（{row['sign_out_at']}）。"

            conn.execute(
                "UPDATE records SET sign_out_at = ?, status = ? WHERE id = ?",
                (now, "已签退", row["id"]),
            )
        return True, f"学号 {student_no} 签退成功，时间 {now}。"

    # ------------------------------------------------------------------ 读取
    def today_record(self, student_no: str) -> Optional[sqlite3.Row]:
        today = date.today().isoformat()
        with self._connect() as conn:
            return conn.execute(
                "SELECT * FROM records WHERE student_no = ? AND sign_date = ?",
                (student_no, today),
            ).fetchone()

    def list_records(self, sign_date: Optional[str] = None) -> list[sqlite3.Row]:
        sql = "SELECT * FROM records"
        params: tuple = ()
        if sign_date:
            sql += " WHERE sign_date = ?"
            params = (sign_date,)
        sql += " ORDER BY sign_date DESC, sign_in_at DESC, id DESC"
        with self._connect() as conn:
            return conn.execute(sql, params).fetchall()

    def stats(self, sign_date: Optional[str] = None) -> dict:
        sign_date = sign_date or date.today().isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM records WHERE sign_date = ?", (sign_date,)
            ).fetchall()
            total_all = conn.execute("SELECT COUNT(*) AS c FROM records").fetchone()["c"]

        signed_in = len(rows)
        signed_out = sum(1 for r in rows if r["sign_out_at"])
        # 约定：09:00 之后签到算迟到
        late = 0
        for r in rows:
            if r["sign_in_at"] and r["sign_in_at"][11:16] > "09:00":
                late += 1
        return {
            "date": sign_date,
            "signed_in": signed_in,
            "signed_out": signed_out,
            "late": late,
            "total_all": total_all,
        }

    def all_dates(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT sign_date FROM records ORDER BY sign_date DESC"
            ).fetchall()
        return [r["sign_date"] for r in rows]

    def clear_today(self) -> int:
        """重置当天数据（供演示 / 测试使用）。"""
        today = date.today().isoformat()
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM records WHERE sign_date = ?", (today,))
        return cur.rowcount
