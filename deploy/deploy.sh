#!/bin/bash
# ============================================
# Django 气象项目 Linux 部署脚本
# 适用于 CentOS 7 / Ubuntu 20.04+
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="weather"
PROJECT_DIR="/opt/weather"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_VERSION="python3"
GUNICORN_WORKERS=4
GUNICORN_PORT=8000

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Django 气象项目部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检测系统类型
detect_os() {
    if [ -f /etc/redhat-release ]; then
        OS="centos"
        PKG_MANAGER="yum"
    elif [ -f /etc/lsb-release ]; then
        OS="ubuntu"
        PKG_MANAGER="apt"
    else
        echo -e "${RED}不支持的操作系统${NC}"
        exit 1
    fi
    echo -e "${GREEN}检测到系统: $OS${NC}"
}

# 安装系统依赖
install_dependencies() {
    echo -e "${YELLOW}[1/7] 安装系统依赖...${NC}"
    
    if [ "$OS" = "centos" ]; then
        sudo yum update -y
        sudo yum install -y epel-release
        sudo yum install -y python3 python3-pip python3-devel \
            mysql-devel gcc nginx git
    else
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv python3-dev \
            default-libmysqlclient-dev build-essential nginx git
    fi
    
    echo -e "${GREEN}系统依赖安装完成${NC}"
}

# 创建项目目录
setup_project_dir() {
    echo -e "${YELLOW}[2/7] 设置项目目录...${NC}"
    
    # 获取脚本所在目录的上级目录（项目根目录）
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SOURCE_DIR="$(dirname "$SCRIPT_DIR")"
    
    # 如果已经在目标目录，跳过复制
    if [ "$SOURCE_DIR" = "$PROJECT_DIR" ]; then
        echo -e "${GREEN}项目已在 $PROJECT_DIR，跳过复制${NC}"
    elif [ -f "$SOURCE_DIR/manage.py" ]; then
        sudo mkdir -p $PROJECT_DIR
        sudo chown -R $USER:$USER $PROJECT_DIR
        # 使用 rsync 或 cp，忽略错误
        cp -rf "$SOURCE_DIR"/* $PROJECT_DIR/ 2>/dev/null || true
        echo -e "${GREEN}项目文件已复制到 $PROJECT_DIR${NC}"
    else
        echo -e "${YELLOW}请手动将项目文件复制到 $PROJECT_DIR${NC}"
    fi
    
    # 创建日志目录
    mkdir -p $PROJECT_DIR/logs
    
    echo -e "${GREEN}项目目录设置完成${NC}"
}

# 创建虚拟环境并安装依赖
setup_virtualenv() {
    echo -e "${YELLOW}[3/7] 创建 Python 虚拟环境...${NC}"
    
    cd $PROJECT_DIR
    $PYTHON_VERSION -m venv $VENV_DIR
    source $VENV_DIR/bin/activate
    
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    
    echo -e "${GREEN}Python 环境配置完成${NC}"
}

# 配置 Django
configure_django() {
    echo -e "${YELLOW}[4/7] 配置 Django...${NC}"
    
    cd $PROJECT_DIR
    source $VENV_DIR/bin/activate
    
    # 数据库迁移
    python manage.py makemigrations china_weather --noinput || true
    python manage.py migrate --noinput
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    echo -e "${GREEN}Django 配置完成${NC}"
}

# 配置 Gunicorn systemd 服务
setup_gunicorn() {
    echo -e "${YELLOW}[5/7] 配置 Gunicorn 服务...${NC}"
    
    sudo tee /etc/systemd/system/weather.service > /dev/null <<EOF
[Unit]
Description=Weather Django Application
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers $GUNICORN_WORKERS --bind 0.0.0.0:$GUNICORN_PORT weather.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable weather
    sudo systemctl start weather
    
    echo -e "${GREEN}Gunicorn 服务配置完成${NC}"
}

# 配置 Nginx
setup_nginx() {
    echo -e "${YELLOW}[6/7] 配置 Nginx...${NC}"
    
    sudo tee /etc/nginx/conf.d/weather.conf > /dev/null <<EOF
server {
    listen 80;
    server_name _;  # 改为你的域名或 IP

    # 静态文件
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django 应用
    location / {
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
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
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    echo -e "${GREEN}Nginx 配置完成${NC}"
}

# 配置防火墙
setup_firewall() {
    echo -e "${YELLOW}[7/7] 配置防火墙...${NC}"
    
    if [ "$OS" = "centos" ]; then
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --reload
    else
        sudo ufw allow 'Nginx HTTP'
        sudo ufw allow 8000/tcp
    fi
    
    echo -e "${GREEN}防火墙配置完成${NC}"
}

# 显示部署结果
show_result() {
    # 获取 IP 地址
    IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  部署完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "访问地址: ${YELLOW}http://$IP${NC}"
    echo -e "直接访问: ${YELLOW}http://$IP:$GUNICORN_PORT${NC}"
    echo ""
    echo -e "常用命令:"
    echo -e "  查看状态: ${YELLOW}sudo systemctl status weather${NC}"
    echo -e "  重启服务: ${YELLOW}sudo systemctl restart weather${NC}"
    echo -e "  查看日志: ${YELLOW}sudo journalctl -u weather -f${NC}"
    echo ""
}

# 主函数
main() {
    detect_os
    install_dependencies
    setup_project_dir
    setup_virtualenv
    configure_django
    setup_gunicorn
    setup_nginx
    setup_firewall
    show_result
}

# 运行
main
