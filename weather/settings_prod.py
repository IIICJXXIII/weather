"""
Django 生产环境配置文件
部署到 Linux 服务器时使用此配置
"""

from .settings import *
import os

# ============================================
# 安全配置
# ============================================

# 关闭调试模式
DEBUG = False

# 允许的主机名（修改为你的服务器 IP 或域名）
ALLOWED_HOSTS = [
    '192.168.56.101',    # VMware 虚拟机 IP
    '127.0.0.1',
    'localhost',
    '*',                  # 允许所有主机（开发测试用，生产环境建议指定具体域名）
]

# 生产环境密钥（建议使用环境变量）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 
    'django-insecure-_wvw5bvw%y1_du=1-y$9p#og53k!0%l3f6(^7ev@2!!c!zav!i')

# ============================================
# 数据库配置
# ============================================

# 使用 MySQL 数据库（与开发环境相同）
# 部署到 Linux 后，连接本机 MySQL，可改为 127.0.0.1
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'china_all',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',  # 部署到同一台服务器，使用本地连接
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# ============================================
# 静态文件配置
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 静态文件目录
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ============================================
# 安全设置
# ============================================

# HTTPS 设置（如果使用 HTTPS）
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# HSTS 设置
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# 其他安全设置
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ============================================
# 日志配置
# ============================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 确保日志目录存在
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ============================================
# 时区和语言
# ============================================

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True
