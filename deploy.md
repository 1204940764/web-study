# 部署指南

## 一、购买服务器（腾讯云轻量应用服务器 ¥88/年）

1. 访问 cloud.tencent.com，注册账号（新用户首年 ¥88）
2. 产品 → 轻量应用服务器 → 购买
   - 地域：选离你最近的
   - 镜像：**Ubuntu 22.04**（不要选应用镜像）
   - 套餐：1核1G，3M带宽
   - 时长：1年
3. 支付，等待创建完成

## 二、购买域名（.top ¥9/年）

1. 腾讯云 → 域名注册 → 搜索 .top 域名
2. 选一个满意的，加入购物车，支付
3. 完成域名实名认证（上传身份证，几分钟审核通过）

## 三、服务器环境配置

SSH 连接到服务器后，依次执行：

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装 Python 和相关工具
sudo apt install python3 python3-pip python3-venv nginx git mysql-server -y

# 3. 配置 MySQL
sudo mysql_secure_installation
# 按提示：设置 root 密码，全部选 Y

# 4. 创建数据库
sudo mysql -u root -p
CREATE DATABASE photo_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'photoblog'@'localhost' IDENTIFIED BY '你的数据库密码';
GRANT ALL PRIVILEGES ON photo_blog.* TO 'photoblog'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 5. 创建项目目录
mkdir -p /home/ubuntu/photo-blog
```

## 四、部署代码

在本地电脑执行（将代码传到服务器）：

```bash
# 本地打包代码
cd /Users/lujiawei/Desktop/项目代码/web网页
tar --exclude='.git' --exclude='__pycache__' --exclude='venv' --exclude='.env' \
    -czf /tmp/photo-blog.tar.gz .

# 上传到服务器（替换为你的服务器 IP）
scp /tmp/photo-blog.tar.gz ubuntu@你的服务器IP:/home/ubuntu/
```

在服务器上执行：

```bash
cd /home/ubuntu/photo-blog
tar -xzf ../photo-blog.tar.gz

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建 .env 配置文件
cat > .env << 'EOF'
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=mysql+pymysql://photoblog:你的数据库密码@localhost:3306/photo_blog?charset=utf8mb4
MAIL_USERNAME=你的QQ邮箱@qq.com
MAIL_PASSWORD=你的QQ邮箱SMTP授权码
EOF

# 初始化数据库
python init_db.py

# 创建上传目录
mkdir -p app/static/uploads
```

## 五、配置 Gunicorn + systemd

```bash
# 创建 systemd 服务
sudo tee /etc/systemd/system/photo-blog.service << 'EOF'
[Unit]
Description=Photo Blog Flask App
After=network.target mysql.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/photo-blog
ExecStart=/home/ubuntu/photo-blog/venv/bin/gunicorn -w 2 -b 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable photo-blog
sudo systemctl start photo-blog

# 检查状态
sudo systemctl status photo-blog
```

## 六、配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/photo-blog << 'EOF'
server {
    listen 80;
    server_name 你的域名.top www.你的域名.top;

    client_max_body_size 16M;

    location /static {
        alias /home/ubuntu/photo-blog/app/static;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/photo-blog /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 七、域名绑定

1. 腾讯云控制台 → 域名管理 → 解析
2. 添加记录：
   - 主机记录：`@`，记录类型：A，记录值：你的服务器 IP
   - 主机记录：`www`，记录类型：A，记录值：你的服务器 IP
3. 等待几分钟 DNS 生效

## 八、SSL 证书（免费）

```bash
# 使用 certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d 你的域名.top -d www.你的域名.top
# 按提示操作，选择自动重定向 HTTP → HTTPS
```

## 九、ICP 备案（必需）

1. 腾讯云控制台 → 备案管理 → 开始备案
2. 按提示填写信息、上传身份证
3. 腾讯云初审（1 天）→ 管局审核（10-15 个工作日）
4. **备案期间不要关闭服务器**

备案通过后，域名即可正常访问。

## 十、QQ 邮箱 SMTP 配置

1. 登录 QQ 邮箱 → 设置 → 账户
2. 开启 POP3/SMTP 服务
3. 获取授权码（16 位）
4. 填入服务器 .env 的 MAIL_PASSWORD

## 快速检查清单

- [ ] 服务器能 ping 通
- [ ] `systemctl status photo-blog` 显示 running
- [ ] `curl http://127.0.0.1:8000/` 返回 HTML
- [ ] 域名解析生效（ping 域名返回 IP）
- [ ] 浏览器访问 http://你的域名 能看到首页
- [ ] SSL 证书生效（https 正常）
- [ ] 注册功能正常（能收到验证码）
- [ ] 管理员登录 admin@qq.com 后台可用
