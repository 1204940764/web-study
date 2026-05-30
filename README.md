# 光影记录

一个基于 Flask 的摄影作品分享社区，支持用户注册、上传照片、评论互动，以及完整的后台管理系统。

**线上地址**: [https://lujiawei.art](https://lujiawei.art)

## 功能

- 邮箱验证码注册/登录
- 照片上传（自动压缩 + 缩略图生成 + EXIF 方向修正）
- 审核模式：管理员可选择开启或关闭，关闭后用户可直接发布
- 三级身份体系：普通用户 / 管理员 / 超级管理员
- 图片评论、用户建议、公告弹窗
- 全站雪花粒子特效
- PWA 可安装到手机桌面（开发中）

## 技术栈

| 分类 | 技术 |
|------|------|
| 后端框架 | Flask 3.0 |
| 数据库 | MySQL 8.0 + SQLAlchemy + PyMySQL |
| 前端 | Jinja2 模板 + Tailwind CSS CDN |
| 认证 | Flask-Login + Werkzeug scrypt |
| 邮件 | Flask-Mail + QQ SMTP |
| 图片处理 | Pillow（压缩、缩略图、EXIF 旋转） |

## 环境要求

- Python 3.10+
- MySQL 8.0+

## 本地开发

```bash
# 1. 克隆项目
git clone git@github.com:1204940764/web-study.git
cd web-study

# 2. 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 创建数据库
mysql -u root -p < init.sql

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 SECRET_KEY、数据库密码、QQ邮箱 SMTP 授权码

# 5. 初始化数据库表 + 创建超级管理员
python3 init_db.py

# 6. 创建上传目录
mkdir -p app/static/uploads

# 7. 启动开发服务器
python3 run.py
# 默认运行在 http://localhost:7373
```

## .env 配置说明

```
SECRET_KEY=随机字符串，用于 session 加密
DATABASE_URL=mysql+pymysql://用户名:密码@主机地址:3306/photo_blog
MAIL_USERNAME=QQ邮箱地址，用于发送验证码
MAIL_PASSWORD=QQ邮箱 SMTP 授权码（不是登录密码）
```

QQ 邮箱 SMTP 开启方式：邮箱设置 → 账户 → POP3/SMTP 服务 → 开启并获取授权码。

## 首次登录

运行 `init_db.py` 后会创建超级管理员账号：

- 邮箱: `admin`
- 密码: `123456`

登录后进入 `/admin` 管理后台，可管理用户、审核照片、发布公告等。

## 目录结构

```
web网页/
├── app/
│   ├── __init__.py          # 应用工厂 + Jinja 过滤器
│   ├── extensions.py        # Flask 扩展初始化
│   ├── models.py            # 数据模型 (7 个表)
│   ├── utils.py             # 邮件发送、图片处理
│   ├── decorators.py        # 权限装饰器
│   ├── auth/routes.py       # 注册/登录/忘记密码
│   ├── main/routes.py       # 首页/详情/搜索/建议
│   ├── photos/routes.py     # 上传/评论/删除
│   ├── user/routes.py       # 个人中心
│   ├── admin/routes.py      # 管理后台
│   ├── static/uploads/      # 上传的图片
│   └── templates/           # Jinja2 模板
├── config.py                # 应用配置
├── run.py                   # 开发服务器入口
├── init_db.py               # 数据库初始化脚本
├── init.sql                 # SQL 建表脚本
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量模板
└── README.md
```

## 身份体系

| 角色 | 权限 |
|------|------|
| 普通用户 | 上传照片、发表评论、提交建议 |
| 管理员 | 审核照片、禁言/禁止发布、删除评论/照片、管理公告。不能操作其他管理员和超级管理员 |
| 超级管理员 | 管理员全部权限 + 修改用户角色、操作管理员 |
