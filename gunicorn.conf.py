# Gunicorn 配置文件
# 使用方法: gunicorn -c gunicorn.conf.py weather.wsgi:application

import multiprocessing

# 绑定地址
bind = "0.0.0.0:8000"

# 工作进程数（推荐 CPU 核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 超时时间
timeout = 120

# 最大请求数（之后 worker 会重启，防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = "/opt/weather/logs/gunicorn_access.log"
errorlog = "/opt/weather/logs/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "weather_gunicorn"

# 守护进程模式（使用 systemd 时设为 False）
daemon = False

# 预加载应用
preload_app = True

# 环境变量
raw_env = [
    "DJANGO_SETTINGS_MODULE=weather.settings_prod",
]
