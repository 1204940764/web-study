# 个人摄影博客系统 — 设计文档

## 概述

个人照片分享博客。管理员和普通用户两类角色，用户可上传照片、发表评论。QQ 邮箱注册。部署腾讯云轻量服务器，最低成本方案。

## 技术选型

| 项 | 选择 | 理由 |
|----|------|------|
| 后端 | Python Flask + Jinja2 | 开发快，生态全 |
| 数据库 | MySQL 8.0 (服务器自建) | 免费，自建无额外费用 |
| ORM | Flask-SQLAlchemy + PyMySQL | |
| 邮箱 | QQ 邮箱 SMTP | 免费，国内可用 |
| 服务器 | 腾讯云轻量 1核1G | 新用户 ¥88/年 |
| 域名 | .top | ¥9/年 |
| 部署 | Nginx + Gunicorn | 经典组合 |
| 前端 | Jinja2 模板 + Tailwind CSS (CDN) | 无需构建工具，绿色主题 |

## 系统架构

单机部署，所有服务在同一台服务器：

```
Nginx (80/443) → Gunicorn → Flask App → MySQL
                                      → 本地文件存储 (uploads/)
                                      → QQ SMTP (发验证码)
```

## 数据模型

### users
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| email | String(120) | QQ邮箱，唯一，用于登录 |
| username | String(64) | 用户自定义，可随时修改 |
| password_hash | String(256) | Werkzeug 哈希 |
| is_admin | Boolean | 默认 False，admin 用户手动在数据库设置 |
| created_at | DateTime | 注册时间 |

### photos
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| user_id | FK → users.id | 上传者 |
| title | String(128) | 照片标题 |
| description | Text | 照片描述 |
| filename | String(256) | 服务器上的文件路径 |
| status | String(16) | pending / approved / rejected |
| created_at | DateTime | |

### comments
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| user_id | FK → users.id | 评论者 |
| photo_id | FK → photos.id | |
| content | Text | 评论内容 |
| created_at | DateTime | |

### email_verifications
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| email | String(120) | |
| code | String(6) | 6位验证码 |
| expires_at | DateTime | 有效期 10 分钟 |
| used | Boolean | 默认 False |

## 路由设计

| 路由 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/` | GET | 首页，照片网格，只显示 approved | 公开 |
| `/photo/<id>` | GET | 照片详情 + 评论 | 公开 |
| `/photo/<id>/comment` | POST | 发表评论 | 登录 |
| `/register` | GET/POST | 注册 | 公开 |
| `/register/send-code` | POST | 发送邮箱验证码 | 公开 |
| `/login` | GET/POST | 登录 | 公开 |
| `/logout` | GET | 退出 | 登录 |
| `/upload` | GET/POST | 上传照片 | 登录 |
| `/profile` | GET/POST | 个人信息 + 修改用户名 | 登录 |
| `/profile/photos` | GET | 我上传的照片 | 登录 |
| `/admin` | GET | 管理后台首页 | 管理员 |
| `/admin/users` | GET/POST | 用户管理（删除、禁用） | 管理员 |
| `/admin/comments` | GET/POST | 评论管理（删除） | 管理员 |
| `/admin/photos` | GET/POST | 审核照片（通过/拒绝） | 管理员 |
| `/search` | GET | 搜索照片（标题/描述） | 公开 |

## 关键业务规则

- QQ邮箱注册：每个邮箱只能注册一个账号
- 验证码 6 位数字，有效期 10 分钟，用完即失效
- 用户可随时修改自己的用户名，无限制
- 照片上传后状态为 pending，需管理员审核通过才在首页展示
- 管理员通过数据库字段 `is_admin=True` 设定，无注册入口
- 评论无需审核，但管理员可删除

## 视觉主题

- "绿色盎然，生机勃勃" —— 主色调绿色系
- 首页照片瀑布流/网格布局
- Tailwind CSS CDN，响应式设计
- 自然、清新、简洁风格

## 部署流程

1. 腾讯云购买轻量应用服务器（¥88/年）
2. 安装 Python 3、Nginx、Git、MySQL 8.0
3. 创建数据库和用户，克隆代码，pip install 依赖
4. 配置 systemd 服务（Gunicorn）
5. 配置 Nginx 反向代理
6. 购买域名 (.top)，DNS 解析到服务器 IP
7. 申请免费 SSL（Let's Encrypt / 腾讯云）
8. 提交 ICP 备案，等待约 10-15 工作日

## 成本汇总

| 项目 | 费用 |
|------|------|
| 服务器 | ¥88/年 (腾讯云轻量新用户) |
| 域名 | ¥9/年 (.top) |
| 数据库 | ¥0 (服务器自建 MySQL) |
| 邮箱 | ¥0 (QQ SMTP) |
| SSL | ¥0 (Let's Encrypt) |
| **首年总计** | **≈ ¥97** |
