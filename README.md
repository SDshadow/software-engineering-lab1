# 课堂签到系统（Sign-in System）

> 软件工程课内实验一《软件工具的使用》实践项目
> 浙江工业大学 计算机科学与技术学院

## 一、项目背景与目标

课堂点名依赖教师人工记录，存在效率低、易遗漏、难以统计的问题。本项目实现一个
**轻量的课堂签到系统**，用于完成实验一中「项目创建 → 代码下载/编写 → 本地运行 →
Git 版本控制 → 开源托管」的完整工程化流程。

项目目标：

1. 掌握 Python + Flask 项目的创建与本地运行方法；
2. 使用 Git 完成初始化、提交、推送等版本控制基本操作；
3. 在 GitHub 上建立开源项目，规范编写项目说明（README）；
4. 借助 AI 编程工具完成一次最小程序编写与一次小功能扩展，建立「人主导、AI 辅助」的开发认知。

## 二、功能说明

| 功能 | 说明 | 入口 |
| --- | --- | --- |
| 学生签到 | 输入学号 + 姓名完成签到，记录精确到秒 | 首页 `/` |
| 学生签退 | 对当天已签到的学号补充签退时间 | 首页 `/` |
| 防重复签到 | 同一学号同一天只允许签到一次，重复提交给出明确提示 | 首页 `/` |
| 查询今日状态 | 按学号查询当天签到 / 签退情况 | 首页 `/` |
| 签到记录列表 | 按日期查看全部签到明细，标记是否迟到 | `/records` |
| 数据统计 | 今日签到人数、已签退人数、迟到人数、累计记录数 | 首页 / `/records` |
| 导出 CSV | 将指定日期的签到记录导出为 CSV（含 BOM，Excel 可直接打开） | `/export.csv` |
| JSON 接口 | `POST /api/signin`、`POST /api/signout`、`GET /api/records`、`GET /api/stats` | — |

业务约定：**09:00 之后签到记为迟到**（阈值写在 `store.py` 的 `stats()` 中，便于修改）。

## 三、技术栈

- **语言**：Python 3（实测 3.13.12）
- **Web 框架**：Flask
- **数据库**：SQLite 3（Python 标准库自带，无需额外安装服务）
- **前端**：Jinja2 模板 + 原生 HTML / CSS
- **版本控制**：Git + GitHub

## 四、运行方式

```bash
# 1. 进入项目目录
cd signin-system

# 2. 安装依赖（建议使用虚拟环境）
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt

# 3. 启动服务
python app.py

# 4. 浏览器访问
#    http://127.0.0.1:5000
```

数据库文件 `data/signin.db` 在首次启动时自动创建，无需手动建表。

### 命令行小程序的运行（AI 初体验任务）

```bash
python hello_ai.py
python hello_ai.py --name 张三
```

### 接口自测

```bash
curl -X POST http://127.0.0.1:5000/api/signin -H "Content-Type: application/json" -d "{\"student_no\":\"3020235111\",\"name\":\"张三\"}"
curl http://127.0.0.1:5000/api/stats
```

## 五、目录结构

```
signin-system/
├─ app.py                 # 应用入口 / 路由控制层
├─ store.py               # 数据访问层（SQLite 建表与读写）
├─ hello_ai.py            # AI 初体验：最小命令行程序
├─ requirements.txt       # 依赖清单
├─ .gitignore             # 忽略规则（数据库、缓存、虚拟环境）
├─ templates/
│  ├─ base.html           # 公共布局（顶栏 / 页脚 / 消息提示）
│  ├─ index.html          # 签到页面
│  └─ records.html        # 签到记录页面
├─ static/css/style.css   # 样式表
└─ docs/
   ├─ screenshots/        # 运行截图
   ├─ GIT_LOG.md          # Git 操作记录
   └─ AI_PROMPTS.md       # AI 提示词与人工校验记录
```

## 六、数据库设计

```sql
CREATE TABLE records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_no  TEXT    NOT NULL,          -- 学号
    name        TEXT    NOT NULL,          -- 姓名
    sign_date   TEXT    NOT NULL,          -- 签到日期 YYYY-MM-DD
    sign_in_at  TEXT,                      -- 签到时间
    sign_out_at TEXT,                      -- 签退时间
    status      TEXT    NOT NULL DEFAULT '已签到',
    UNIQUE (student_no, sign_date)         -- 同一学号同一天唯一
);
```

`UNIQUE(student_no, sign_date)` 既是业务规则，也是最后一道数据完整性防线。
除了这条约束，业务层还做了显式校验，以便给用户返回可读的提示而不是数据库异常。

## 七、运行截图

见 `docs/screenshots/` 目录，例如：

| 文件 | 说明 |
| --- | --- |
| `01-签到界面.png` | 系统首页（签到表单 + 今日状态） |
| `02-签到成功.png` | 签到成功提示与状态回显 |
| `03-重复签到拦截.png` | 同一学号重复签到的拦截提示 |
| `04-签到记录.png` | 签到记录列表与统计 |
| `05-命令行运行.png` | `python app.py` 启动与 `hello_ai.py` 运行结果 |

## 八、AI 使用情况

本次实验使用 AI 编程工具辅助完成以下工作，所有生成代码均经人工阅读、运行验证与修改：

| 环节 | AI 用途 | 人工校验 |
| --- | --- | --- |
| 最小程序 | 生成 `hello_ai.py` 初版（输出「Hello, AI 编程！」） | 本地运行确认输出；补充 `--name` 参数与时间打印 |
| 签到系统骨架 | 生成 Flask 路由与 Jinja2 模板骨架 | 逐行阅读，补充分层（`store.py`）与错误提示 |
| 功能扩展 | 生成「防重复签到 + 迟到判定 + CSV 导出」 | 构造重复签到用例验证；确认 09:00 阈值逻辑 |

详细的提示词与人工修改点见 `docs/AI_PROMPTS.md`。

## 九、开发与提交记录

Git 操作记录见 `docs/GIT_LOG.md`，提交遵循「每个阶段一次提交」的规范，便于追溯。

## 十、许可

本项目为课程实验作品，仅用于教学演示。
