# -*- coding: utf-8 -*-
"""签到系统 —— 软件工程实验一「软件工具的使用」

技术栈：Python 3 + Flask + SQLite（均为免费开源工具）
运行方式：
    1) pip install -r requirements.txt
    2) python app.py
    3) 浏览器访问 http://127.0.0.1:5000

分层说明：
    store.py  ->  数据访问层（SQLite）
    app.py    ->  路由 / 控制层
    templates ->  视图层（Jinja2 模板）
    static    ->  静态资源（CSS / JS）
"""
from __future__ import annotations

import csv
import io
import os
from datetime import date

from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for)

from store import Store

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "sign-in-system-demo-key"      # 仅用于 flash 提示，演示用
# Flask 3.x 用 app.json.ensure_ascii 控制 JSON 是否转义非 ASCII 字符
app.json.ensure_ascii = False

store = Store(os.path.join(BASE_DIR, "data", "signin.db"))

DEFAULT_DATE = None                              # None 表示「今天」


def _target_date() -> str | None:
    """从查询参数读取要查看的日期，缺省为今天。"""
    d = request.args.get("date", "").strip()
    return d or None


# ====================================================================== 页面
@app.route("/")
def index():
    """签到页面：填写学号与姓名进行签到 / 签退。"""
    student_no = request.args.get("no", "").strip()
    record = store.today_record(student_no) if student_no else None
    return render_template(
        "index.html",
        today=date.today().isoformat(),
        student_no=student_no,
        record=record,
        stats=store.stats(),
    )


@app.route("/records")
def records():
    """签到记录页面：列表 + 统计 + 导出入口。"""
    target = _target_date()
    return render_template(
        "records.html",
        rows=store.list_records(target),
        stats=store.stats(target),
        dates=store.all_dates(),
        current_date=target or date.today().isoformat(),
    )


# ================================================================ 表单行为
@app.route("/signin", methods=["POST"])
def signin():
    student_no = (request.form.get("student_no") or "").strip()
    name = (request.form.get("name") or "").strip()

    if not student_no or not name:
        flash("学号和姓名都不能为空。", "error")
        return redirect(url_for("index"))

    ok, message = store.sign_in(student_no, name)
    flash(message, "ok" if ok else "error")
    return redirect(url_for("index", no=student_no))


@app.route("/signout", methods=["POST"])
def signout():
    student_no = (request.form.get("student_no") or "").strip()
    if not student_no:
        flash("请先填写学号。", "error")
        return redirect(url_for("index"))

    ok, message = store.sign_out(student_no)
    flash(message, "ok" if ok else "error")
    return redirect(url_for("index", no=student_no))


# ==================================================================== API
@app.route("/api/signin", methods=["POST"])
def api_signin():
    """JSON 接口：签到。供脚本 / 自动化测试调用。"""
    data = request.get_json(silent=True) or request.form
    student_no = (data.get("student_no") or "").strip()
    name = (data.get("name") or "").strip()
    if not student_no or not name:
        return jsonify({"ok": False, "message": "学号和姓名都不能为空。"}), 400
    ok, message = store.sign_in(student_no, name)
    return jsonify({"ok": ok, "message": message}), (200 if ok else 409)


@app.route("/api/signout", methods=["POST"])
def api_signout():
    data = request.get_json(silent=True) or request.form
    student_no = (data.get("student_no") or "").strip()
    if not student_no:
        return jsonify({"ok": False, "message": "请先填写学号。"}), 400
    ok, message = store.sign_out(student_no)
    return jsonify({"ok": ok, "message": message}), (200 if ok else 409)


@app.route("/api/records")
def api_records():
    target = _target_date()
    rows = [dict(r) for r in store.list_records(target)]
    return jsonify({"ok": True, "count": len(rows), "records": rows})


@app.route("/api/stats")
def api_stats():
    return jsonify({"ok": True, **store.stats(_target_date())})


@app.route("/health")
def health():
    return jsonify({"ok": True, "service": "signin-system", "date": date.today().isoformat()})


# =================================================================== 导出
@app.route("/export.csv")
def export_csv():
    target = _target_date()
    rows = store.list_records(target)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["学号", "姓名", "日期", "签到时间", "签退时间", "状态"])
    for r in rows:
        writer.writerow([r["student_no"], r["name"], r["sign_date"],
                         r["sign_in_at"] or "", r["sign_out_at"] or "", r["status"]])

    # 加 BOM，避免 Excel 打开中文乱码
    content = "\ufeff" + buf.getvalue()
    filename = f"signin-records-{target or date.today().isoformat()}.csv"
    return Response(
        content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


if __name__ == "__main__":
    host = os.environ.get("SIGNIN_HOST", "127.0.0.1")
    port = int(os.environ.get("SIGNIN_PORT", "5000"))
    debug = os.environ.get("SIGNIN_DEBUG", "1") == "1"
    print(f"签到系统已启动： http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
