# Git 操作记录（Git Operation Log）

> 本文件记录实验一中所有 Git 操作的实际命令与关键输出，用于报告中的「Git 操作记录」章节。
> 记录时间：2026-09-29　操作者：SDshadow

## 一、环境准备与配置校验

```bash
$ git --version
git version 2.51.2.windows.1

$ git config --global user.name
SDshadow
$ git config --global user.email
2727192251@qq.com
```

## 二、初始化本地仓库

```bash
$ cd signin-system
$ git init -b main
Initialized empty Git repository in D:/.../signin-system/.git/

$ git status --short
?? .gitignore
?? README.md
?? app.py
?? docs/
?? hello_ai.py
?? requirements.txt
?? static/
?? store.py
?? templates/
?? tools/
```

> 说明：`data/`（SQLite 数据库目录）未出现在待提交列表中，说明 `.gitignore` 生效。

## 三、分阶段提交（每完成一个模块提交一次）

```bash
$ git add .gitignore README.md requirements.txt
$ git commit -m "chore: 初始化签到系统仓库"
$ git add store.py
$ git commit -m "feat(store): 新增 SQLite 数据访问层"
$ git add app.py templates static
$ git commit -m "feat(web): 实现签到页面、记录页面与 REST 接口"
$ git add hello_ai.py docs/AI_PROMPTS.md
$ git commit -m "feat(ai): 添加 AI 编程初体验程序与提示词记录"
$ git add tools docs/screenshots
$ git commit -m "docs: 添加演示数据脚本与系统运行截图"
```

提交历史：

| 提交号 | 时间 | 提交信息 | 变更规模 |
| --- | --- | --- | --- |
| `ebca3fd` | 2026-09-29 14:13:33 | chore: 初始化签到系统仓库 | 3 文件 / +167 |
| `cae4879` | 2026-09-29 14:13:35 | feat(store): 新增 SQLite 数据访问层 | 1 文件 / +146 |
| `40c78b1` | 2026-09-29 14:13:36 | feat(web): 实现签到页面、记录页面与 REST 接口 | 5 文件 / +598 |
| `d05b7ff` | 2026-09-29 14:13:38 | feat(ai): 添加 AI 编程初体验程序与提示词记录 | 2 文件 / +145 |
| `3574445` | 2026-09-29 14:13:39 | docs: 添加演示数据脚本与系统运行截图 | 6 文件 / +73 |

## 四、创建远程仓库并推送

```bash
$ gh repo create software-engineering-lab1 --public \
    --description "软件工程实验一：课堂签到系统（Python + Flask + SQLite），含 Git 版本控制与 AI 辅助编程实践"
https://github.com/SDshadow/software-engineering-lab1

$ git remote add origin git@github.com:SDshadow/software-engineering-lab1.git
$ git remote -v
origin  git@github.com:SDshadow/software-engineering-lab1.git (fetch)
origin  git@github.com:SDshadow/software-engineering-lab1.git (push)

$ git push -u origin main
To github.com:SDshadow/software-engineering-lab1.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

## 五、推送后校验

```bash
$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean

$ git ls-remote --heads origin
35744456e49bf5e652a42e9d5565235ff3c68a4a    refs/heads/main

$ git status --ignored --short
!! data/
```

本地 `HEAD`（`3574445`）与远程 `main`（`3574445`）一致，工作区干净，
数据库目录被正确忽略。

## 六、远程仓库地址

- 仓库链接：<https://github.com/SDshadow/software-engineering-lab1>

## 七、小结

| 考核点 | 完成情况 |
| --- | --- |
| 仓库初始化 | `git init -b main` |
| 提交信息规范 | 采用 `chore / feat(模块) / docs` 前缀，提交信息说明「做了什么、为什么」 |
| 分阶段提交 | 按「仓库骨架 → 数据层 → 表现层 → AI 程序 → 文档截图」5 次提交，可追溯 |
| 推送到远程 | `git push -u origin main`，本地与远程一致 |
| 忽略无关文件 | `.gitignore` 忽略虚拟环境、`__pycache__`、SQLite 数据库与导出文件 |
