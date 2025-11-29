# Django 气象项目 - Linux 服务器部署指南

## 📋 部署前准备

### 1. 服务器要求
- **操作系统**: CentOS 7/8 或 Ubuntu 20.04+
- **内存**: 建议 2GB+
- **磁盘**: 建议 10GB+
- **Python**: 3.8+

### 2. 网络规划
假设你的 VMware 虚拟机网络配置如下：
- 虚拟机 IP: `192.168.56.101`
- MySQL 数据库: 同一台机器或集群中

---

## 🚀 快速部署（一键脚本）

### 方法一：使用部署脚本

```bash
# 1. 将项目上传到服务器
scp -r weather/ root@192.168.56.101:/opt/

# 2. SSH 登录服务器
ssh root@192.168.56.101

# 3. 进入项目目录并运行部署脚本
cd /opt/weather
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

---

## 📝 手动部署步骤

### 步骤 1: 安装系统依赖

**CentOS 7:**
```bash
# 更新系统
sudo yum update -y

# 安装 EPEL 源
sudo yum install -y epel-release

# 安装 Python 3 和开发工具
sudo yum install -y python3 python3-pip python3-devel gcc mysql-devel

# 安装 Nginx
sudo yum install -y nginx
```

**Ubuntu 20.04:**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3 和开发工具
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 安装 MySQL 开发库
sudo apt install -y default-libmysqlclient-dev build-essential

# 安装 Nginx
sudo apt install -y nginx
```

### 步骤 2: 上传项目文件

**Windows PowerShell:**
```powershell
# 使用 scp 上传（需要安装 OpenSSH 客户端）
scp -r D:\PycharmProject\weather\* root@192.168.56.101:/opt/weather/

# 或者使用 WinSCP / FileZilla 等工具上传
```

**Linux 服务器:**
```bash
# 创建项目目录
sudo mkdir -p /opt/weather
sudo chown -R $USER:$USER /opt/weather
```

### 步骤 3: 配置 Python 虚拟环境

```bash
cd /opt/weather

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 安装 Gunicorn
pip install gunicorn
```

### 步骤 4: 配置 Django

```bash
# 激活虚拟环境（如果未激活）
source /opt/weather/.venv/bin/activate

cd /opt/weather

# 创建日志目录
mkdir -p logs

# 数据库迁移
python manage.py makemigrations china_weather
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级用户（可选）
python manage.py createsuperuser
```

### 步骤 5: 修改配置文件

编辑 `weather/settings_prod.py`，修改以下配置：

```python
# 修改为你的服务器 IP
ALLOWED_HOSTS = [
    '192.168.56.101',
    '127.0.0.1',
    'localhost',
]
```

### 步骤 6: 测试运行

```bash
# 使用生产配置启动
export DJANGO_SETTINGS_MODULE=weather.settings_prod

# 测试 Gunicorn
gunicorn --bind 0.0.0.0:8000 weather.wsgi:application

# 访问 http://192.168.56.101:8000 测试
# Ctrl+C 停止
```

### 步骤 7: 配置 Systemd 服务

```bash
# 创建服务文件
sudo tee /etc/systemd/system/weather.service > /dev/null <<EOF
[Unit]
Description=Weather Django Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/weather
Environment="PATH=/opt/weather/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=weather.settings_prod"
ExecStart=/opt/weather/.venv/bin/gunicorn -c gunicorn.conf.py weather.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start weather

# 设置开机自启
sudo systemctl enable weather

# 查看状态
sudo systemctl status weather
```

### 步骤 8: 配置 Nginx

```bash
# 创建 Nginx 配置
sudo tee /etc/nginx/conf.d/weather.conf > /dev/null <<EOF
server {
    listen 80;
    server_name 192.168.56.101;  # 改为你的 IP 或域名

    # 静态文件
    location /static/ {
        alias /opt/weather/staticfiles/;
        expires 30d;
    }

    # 代理 Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 步骤 9: 配置防火墙

**CentOS 7 (firewalld):**
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**Ubuntu (ufw):**
```bash
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 8000/tcp
sudo ufw enable
```

---

## ✅ 验证部署

```bash
# 1. 检查服务状态
sudo systemctl status weather
sudo systemctl status nginx

# 2. 检查端口
netstat -tlnp | grep -E '80|8000'

# 3. 查看日志
sudo journalctl -u weather -f
tail -f /opt/weather/logs/gunicorn_access.log

# 4. 访问测试
curl http://localhost
curl http://localhost:8000
```

**浏览器访问:**
- http://192.168.56.101 (通过 Nginx)
- http://192.168.56.101:8000 (直接访问 Gunicorn)

---

## 🔧 常用运维命令

```bash
# 重启应用
sudo systemctl restart weather

# 查看日志
sudo journalctl -u weather -f

# 重新加载 Nginx
sudo nginx -s reload

# 进入虚拟环境
source /opt/weather/.venv/bin/activate

# 更新代码后
cd /opt/weather
git pull  # 或手动上传
python manage.py collectstatic --noinput
sudo systemctl restart weather
```

---

## ⚠️ 常见问题

### 1. 静态文件 404
```bash
# 检查静态文件目录
ls -la /opt/weather/staticfiles/

# 重新收集静态文件
python manage.py collectstatic --noinput

# 检查 Nginx 配置中的路径是否正确
```

### 2. 502 Bad Gateway
```bash
# 检查 Gunicorn 是否运行
sudo systemctl status weather

# 查看错误日志
sudo journalctl -u weather -n 50
```

### 3. 数据库连接失败
```bash
# 确保 MySQL 允许远程连接
mysql -u root -p
GRANT ALL PRIVILEGES ON china_all.* TO 'root'@'%' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;

# 检查防火墙
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

### 4. Permission Denied
```bash
# 修复权限
sudo chown -R root:root /opt/weather
chmod -R 755 /opt/weather
```

---

## 📁 部署后目录结构

```
/opt/weather/
├── .venv/                 # Python 虚拟环境
├── china_weather/         # Django 应用
├── weather/               # Django 项目配置
│   ├── settings.py        # 开发配置
│   └── settings_prod.py   # 生产配置
├── templates/             # HTML 模板
├── static/                # 静态资源（开发）
├── staticfiles/           # 静态资源（生产，collectstatic 生成）
├── logs/                  # 日志目录
│   ├── django.log
│   ├── gunicorn_access.log
│   └── gunicorn_error.log
├── db.sqlite3             # SQLite 数据库
├── gunicorn.conf.py       # Gunicorn 配置
├── manage.py
└── requirements.txt
```

---

## 🔒 安全建议

1. **修改 SECRET_KEY**: 使用环境变量存储
2. **关闭 DEBUG**: 生产环境必须设为 False
3. **使用 HTTPS**: 配置 SSL 证书
4. **定期备份**: 备份数据库和用户数据
5. **限制访问**: 配置防火墙规则
