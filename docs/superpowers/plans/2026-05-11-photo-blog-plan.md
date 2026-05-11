# 个人摄影博客系统 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 搭建一个个人照片分享博客，支持用户注册（QQ邮箱）、上传照片、评论，管理员管理用户和评论。

**Architecture:** Flask + MySQL + Jinja2 模板渲染，单机部署，Flask 蓝图模块化。

**Tech Stack:** Python 3, Flask, Flask-SQLAlchemy, PyMySQL, Flask-Login, Flask-Mail, Tailwind CSS (CDN)

## 文件结构

```
web网页/
├── config.py
├── requirements.txt
├── run.py
├── app/
│   ├── __init__.py         # App 工厂
│   ├── extensions.py       # db, login_manager, mail
│   ├── models.py           # User, Photo, Comment, EmailVerification
│   ├── utils.py            # 验证码生成/发送, 图片保存
│   ├── decorators.py       # admin_required
│   ├── auth/routes.py        # Blueprint: 注册/登录/登出
│   ├── main/routes.py        # Blueprint: 首页/照片详情/搜索
│   ├── photos/routes.py      # Blueprint: 上传/评论
│   ├── user/routes.py        # Blueprint: 个人中心/改用户名
│   ├── admin/routes.py       # Blueprint: 管理后台
│   ├── templates/          # Jinja2 模板
│   └── static/             # CSS + 上传文件
```

## 任务列表

### Task 1: 项目骨架搭建
- 创建目录结构
- requirements.txt（Flask, Flask-SQLAlchemy, PyMySQL, Flask-Login, Flask-Mail, python-dotenv）
- config.py（数据库连接、邮件配置、密钥等）
- app/extensions.py（初始化 db, login_manager, mail）
- app/__init__.py（create_app 工厂函数，注册蓝图）
- run.py（入口）

### Task 2: 数据模型
- app/models.py：User, Photo, Comment, EmailVerification 四个模型
- 初始化数据库脚本

### Task 3-8: 各蓝图路由 + 模板
每个蓝图包含 routes.py + 对应 HTML 模板，按 auth → main → photos → user → admin 顺序实现。

### Task 9: 视觉主题（绿色生机风格）
- base.html 基础模板 + Tailwind CDN
- 绿色系配色方案
- 响应式照片网格

### Task 10: 部署文档
- 腾讯云服务器配置步骤
- Nginx + Gunicorn 配置
- MySQL 安装与建库
- 域名绑定 + SSL

---
