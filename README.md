# NCDC 全国气象数据分析与可视化平台

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Django-3.2%20LTS-green.svg" alt="Django">
  <img src="https://img.shields.io/badge/ECharts-5.x-red.svg" alt="ECharts">
  <img src="https://img.shields.io/badge/Hadoop-2.9.2-yellow.svg" alt="Hadoop">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
</p>

基于 Hadoop 大数据平台的全国气象数据分析与可视化系统，实现从数据采集、存储、计算、挖掘到 Web 可视化展示的全链路解决方案。

---

## 📋 目录

- [项目概述](#-项目概述)
- [功能特性](#-功能特性)
- [系统截图](#-系统截图)
- [技术架构](#-技术架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [功能模块详解](#-功能模块详解)
- [API 接口](#-api-接口)
- [数据库设计](#-数据库设计)
- [运维指南](#-运维指南)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

---

## 🌟 项目概述

### 项目背景

本项目是一个完整的大数据气象分析平台，数据来源于 NCDC（美国国家气候数据中心）公开气象数据集 ISD-Lite，涵盖 2000-2022 年全国各省市的气温、降水、气压、风速等多维度气象指标。

### 核心目标

- 🏗️ 搭建高可用的 Hadoop 大数据集群环境（1 Master + 2 Slaves）
- 🧹 清洗并处理海量非结构化气象数据（10,897 个原始文件）
- 📊 多维度统计分析全国各省市气象指标
- 🔮 利用时序预测算法（Holt-Winters / ARIMA）预测气温趋势
- 🖥️ 通过 Web 大屏进行可视化交互展示

---

## ✨ 功能特性

### 🗺️ 数据可视化大屏
- **交互式中国地图**：气温颜色分级 + 风速散点叠加
- **时间轴轮播**：自动播放 1-12 月数据变化
- **多图表联动**：柱状图、词云图、折线图（含预测曲线）、矩形树图

### 📍 省份数据功能
- **省份列表**：展示全国所有省份气象概览，支持按温度排序
- **省份详情**：包含统计卡片、温度趋势图、历史数据、风向玫瑰图、7天预报
- **历史查询**：按省份和月份查询历史气温、风速、气压数据
- **数据对比**：多省份数据同屏对比分析

### 📈 数据分析模块
- **统计卡片**：全国年均温度、极端高温/低温、最大降水城市、最大风速省份
- **热力图**：省份-月份气温热力分布
- **极端天气排行**：高温/低温 Top 10
- **季节分析**：四季堆叠图、雷达图、箱线图

### 👤 用户系统
- **注册/登录**：完整的用户认证系统
- **个人中心**：查看收藏、浏览历史、账号统计
- **收藏功能**：收藏感兴趣的省份，支持备注
- **浏览历史**：自动记录浏览过的省份
- **账号设置**：修改个人信息、修改密码

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        展示层 (Presentation)                      │
│     Django 3.2 + ECharts 5.x + Bootstrap + 响应式设计              │
├─────────────────────────────────────────────────────────────────┤
│                        应用层 (Application)                       │
│          Django Views + REST API + 用户认证 + 会话管理              │
├─────────────────────────────────────────────────────────────────┤
│                        数据层 (Data Access)                       │
│              SQLAlchemy + Pandas + PyMySQL                       │
├─────────────────────────────────────────────────────────────────┤
│                        存储层 (Storage)                           │
│        MySQL (结果数据) │ SQLite (用户数据) │ HDFS (原始数据)        │
├─────────────────────────────────────────────────────────────────┤
│                        计算层 (Computing)                         │
│              YARN + MapReduce + Hive + Sqoop                     │
├─────────────────────────────────────────────────────────────────┤
│                        基础设施 (Infrastructure)                   │
│          VMware + CentOS 7 (1 Master + 2 Slaves)                 │
└─────────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术选型 | 版本 |
|------|---------|------|
| 前端 | ECharts, Bootstrap, D3.js, WordCloud | 5.x, 3.x |
| 后端 | Django, Python | 3.2.25 LTS, 3.8+ |
| 数据处理 | Pandas, NumPy, SQLAlchemy | 2.3.3, 2.0.2, 2.0.44 |
| 数据库 | MySQL (气象), SQLite (用户) | 5.7+, 内置 |
| 大数据 | Hadoop, Hive, Sqoop | 2.9.2, 2.1.0, 1.4.6 |
| 部署 | VMware, CentOS, Nginx | 7.x |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ (用于气象数据)
- 已配置的 Hadoop 集群 (可选，用于数据处理)

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/IIICJXXIII/weather.git
cd weather

# 2. 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置数据库连接
# 编辑 china_weather/views.py 中的数据库连接字符串
# engine = create_engine('mysql+pymysql://用户名:密码@IP:端口/数据库名')

# 5. 初始化本地数据库（用户系统）
python manage.py makemigrations
python manage.py migrate

# 6. 创建超级用户（可选）
python manage.py createsuperuser

# 7. 启动开发服务器
python manage.py runserver
```

### 访问地址

| 页面 | 地址 |
|------|------|
| 首页大屏 | http://127.0.0.1:8000/ |
| 省份列表 | http://127.0.0.1:8000/province/ |
| 历史查询 | http://127.0.0.1:8000/history/ |
| 数据对比 | http://127.0.0.1:8000/compare/ |
| 数据分析 | http://127.0.0.1:8000/analysis/ |
| 关于项目 | http://127.0.0.1:8000/about/ |
| 用户登录 | http://127.0.0.1:8000/login/ |
| 用户注册 | http://127.0.0.1:8000/register/ |
| 个人中心 | http://127.0.0.1:8000/profile/ |
| 管理后台 | http://127.0.0.1:8000/admin/ |

---

## 📁 项目结构

```
weather/
├── china_weather/              # 主应用目录
│   ├── models.py              # 数据模型（用户收藏、浏览历史等）
│   ├── views.py               # 视图函数（所有业务逻辑）
│   ├── admin.py               # Django Admin 配置
│   └── migrations/            # 数据库迁移文件
│
├── weather/                    # Django 项目配置
│   ├── settings.py            # 项目设置
│   ├── urls.py                # URL 路由配置
│   └── wsgi.py                # WSGI 入口
│
├── templates/                  # HTML 模板
│   ├── base.html              # 基础模板（导航、页脚）
│   ├── index.html             # 首页大屏
│   ├── province_list.html     # 省份列表
│   ├── province_detail.html   # 省份详情
│   ├── history_query.html     # 历史查询
│   ├── compare.html           # 数据对比
│   ├── analysis.html          # 数据分析
│   ├── about.html             # 关于项目
│   ├── login.html             # 用户登录
│   ├── register.html          # 用户注册
│   ├── profile.html           # 个人中心
│   └── settings.html          # 账号设置
│
├── static/                     # 静态资源
│   ├── css/                   # 样式文件
│   │   ├── app.css           # 主样式
│   │   ├── nav.css           # 导航样式
│   │   └── bootstrap.min.css # Bootstrap
│   ├── js/                    # JavaScript
│   │   ├── echarts.min.js    # ECharts 图表库
│   │   ├── china.js          # 中国地图数据
│   │   ├── map_chart.js      # 地图图表
│   │   ├── line_chart.js     # 折线图
│   │   ├── bar_chart.js      # 柱状图
│   │   ├── tree_chart.js     # 矩形树图
│   │   ├── word_chart.js     # 词云图
│   │   ├── timeline.js       # 时间轴控制
│   │   └── total_control.js  # 整体控制
│   └── data/                  # CSV 数据文件
│
├── db.sqlite3                  # SQLite 数据库（用户数据）
├── manage.py                   # Django 管理脚本
├── requirements.txt            # Python 依赖
└── README.md                   # 项目文档
```

---

## 📚 功能模块详解

### 1. 首页数据大屏 (`/`)

展示 2022 年全国各省份气象情况的可视化大屏：

| 图表 | 说明 |
|------|------|
| 中国地图 | 气温颜色分级 + 风速散点图 |
| 时间轴 | 1-12 月自动轮播 |
| 折线图 | 各省份月均气温 + 预测曲线 |
| 柱状图 | 降水量 Top 10 城市 |
| 词云图 | 各城市气温分布 |
| 矩形树图 | 各省份气压分布 |

### 2. 省份列表 (`/province/`)

- 展示全国所有省份的气象概览
- 显示年均温度、平均风速、最高/最低温度
- 按年均温度排序，快速定位

### 3. 省份详情 (`/province/<省份名>/`)

- **统计卡片**：平均气温、最高/最低温、全国排名、平均风速、平均气压、年降水量
- **月度趋势图**：12 个月的温度变化曲线
- **历史数据图**：多年平均温度趋势
- **风向玫瑰图**：8 个方向的风频分布
- **7 天预报**：模拟天气预报展示
- **收藏功能**：登录用户可收藏省份

### 4. 历史查询 (`/history/`)

- 选择省份和月份进行查询
- 返回该省份该月的气温、风速、气压数据

### 5. 数据对比 (`/compare/`)

- 多选省份进行同屏对比
- 对比各省份 12 个月的温度和风速变化

### 6. 数据分析 (`/analysis/`)

- **统计概览**：全国平均温度、极端高/低温记录、最大降水城市、最大风速省份
- **热力图**：省份-月份气温分布
- **极端天气排行**：高温/低温 Top 10
- **季节分析**：四季堆叠图、雷达图、箱线图

### 7. 用户系统

| 功能 | 路由 | 说明 |
|------|------|------|
| 登录 | `/login/` | 用户名密码登录，支持记住我 |
| 注册 | `/register/` | 新用户注册，含表单验证 |
| 登出 | `/logout/` | 安全退出 |
| 个人中心 | `/profile/` | 收藏列表、浏览历史、账号统计 |
| 账号设置 | `/settings/` | 修改信息、修改密码 |

---

## 🔌 API 接口

### 收藏相关

```http
# 切换收藏状态（推荐使用）
POST /api/toggle_favorite/
Content-Type: application/json
X-CSRFToken: <token>

Request:  { "province": "北京" }
Response: { "success": true, "is_favorite": true, "message": "收藏成功" }
Response: { "success": true, "is_favorite": false, "message": "已取消收藏" }
Response: { "success": false, "message": "请先登录", "redirect": "/login/..." }

# 添加收藏
POST /api/favorite/add/
Request:  { "province": "北京", "note": "首都" }
Response: { "success": true, "message": "收藏成功" }

# 取消收藏
POST /api/favorite/remove/
Request:  { "province": "北京" } 或 { "id": 1 }
Response: { "success": true, "message": "已取消收藏" }

# 检查收藏状态
GET /api/favorite/check/?province=北京
Response: { "is_favorite": true, "logged_in": true }
```

---

## 💾 数据库设计

### 气象数据表（MySQL）

| 表名 | 说明 |
|------|------|
| `china_map` | 各省份月度气温、风速数据 |
| `province_temp` | 各省份月度气温 + 预测值 |
| `province_pressure` | 各省份月度气压 |
| `city_temp` | 各城市月度气温 |
| `city_precipitation_top10` | 降水量 Top 10 城市 |
| `province_temp_all` | 历史年度气温数据 |

### 用户数据表（SQLite）

| 表名 | 说明 |
|------|------|
| `auth_user` | Django 内置用户表 |
| `user_profile` | 用户扩展信息（头像、位置、简介） |
| `user_favorite` | 用户收藏（用户-省份-备注） |
| `browse_history` | 浏览历史记录 |

---

## 🔧 运维指南

### Django 配置说明

```python
# weather/settings.py 主要配置

# 数据库配置（用户数据使用 SQLite）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 静态文件
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 模板目录
TEMPLATES = [{'DIRS': [BASE_DIR / 'templates']}]
```

### 气象数据库连接

```python
# china_weather/views.py
# 修改为你的 MySQL 连接信息
engine = create_engine('mysql+pymysql://root:password@192.168.56.101:3306/china_all')
```

### 生产环境部署

```bash
# 1. 收集静态文件
python manage.py collectstatic

# 2. 使用 Gunicorn 启动
gunicorn weather.wsgi:application -b 0.0.0.0:8000

# 3. 配置 Nginx 反向代理
# /etc/nginx/sites-available/weather
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/weather/static/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## ❓ 常见问题

### 1. 启动时报数据库连接错误

**现象**：`Can't connect to MySQL server`

**解决**：
- 检查 MySQL 服务是否启动
- 检查 `views.py` 中的连接字符串配置
- 确保 MySQL 用户有远程访问权限

### 2. 页面数据不显示

**现象**：图表空白或报 `np is not defined`

**解决**：数据类型问题已在代码中修复，确保使用最新版本的 `views.py`

### 3. Django 版本兼容

**现象**：`MySQL 8.0 or later is required`

**解决**：本项目使用 Django 3.2 LTS，兼容 MySQL 5.7

### 4. 静态文件 404

**现象**：CSS/JS 文件加载失败

**解决**：
```python
# settings.py 确保配置正确
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 5. 页面样式不生效

**现象**：CSS 样式没有正确应用

**解决**：检查模板中的 block 名称，必须使用 `extra_head` 而非 `extra_css`：
```html
<!-- 正确 -->
{% block extra_head %}
<style>...</style>
{% endblock %}

<!-- 错误 -->
{% block extra_css %}...{% endblock %}
```

### 6. 登录注册功能异常

**现象**：登录后跳转到首页而非个人中心，或注册后无法登录

**解决**：确保 `views.py` 中使用正确的 auth 函数名：
```python
# 正确：导入时重命名避免与视图函数冲突
from django.contrib.auth import login as auth_login, logout as auth_logout

# 调用时使用重命名后的函数
auth_login(request, user)
auth_logout(request)
```

### 7. 收藏功能 404

**现象**：`POST /api/toggle_favorite/ 404`

**解决**：确保 `urls.py` 中添加了路由：
```python
path('api/toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
```

### 8. 数据分析页面下拉框显示异常

**现象**：省份选择框显示 `[` 字符或乱码

**解决**：使用 JavaScript 动态填充 select 选项，而非 Django 模板循环 JSON 字符串

---

## 📄 依赖清单

```
Django==3.2.25          # Web 框架
pandas==2.3.3           # 数据处理
numpy==2.0.2            # 数值计算
SQLAlchemy==2.0.44      # ORM
PyMySQL==1.1.2          # MySQL 驱动
```

---

## 📝 更新日志

### v2.1.0 (2025-11-28)
- 🐛 修复登录注册功能（解决 `login` 函数命名冲突）
- 🐛 修复收藏功能（添加 `toggle_favorite` API 端点）
- 🐛 修复数据分析页面省份下拉框显示问题
- 🐛 修复所有页面样式不生效问题（`extra_css` → `extra_head`）
- 🎨 优化历史查询、数据对比、关于项目页面居中布局
- 🎨 优化 Tab 按钮和 Filter-bar 样式显示

### v2.0.0 (2025-11)
- ✨ 新增完整用户系统（注册/登录/个人中心）
- ✨ 新增省份收藏功能
- ✨ 新增浏览历史记录
- ✨ 新增省份详情页（统计卡片、多图表、7天预报）
- ✨ 新增数据分析页（热力图、极端天气、季节分析）
- ✨ 新增历史查询和数据对比功能
- 🎨 全新响应式导航设计
- 🎨 统一的深色主题 UI
- 🐛 修复数据类型兼容问题

### v1.0.0 (2024)
- 🎉 初始版本发布
- 📊 数据可视化大屏
- 🗺️ 中国地图 + 时间轴轮播

---

## 📧 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

## 📖 附录：大数据平台搭建与运维

<details>
<summary>点击展开 Hadoop 集群搭建与故障排查指南</summary>

### 项目实施全流程

#### 阶段一：基础设施搭建
- 搭建了 1 Master + 2 Slaves 的 Hadoop 完全分布式集群
- 配置了 SSH 免密登录、JDK 环境、Hadoop 核心参数（`core-site.xml`, `yarn-site.xml` 等）
- 解决了虚拟机网络配置（静态 IP + NAT）、防火墙策略等问题

#### 阶段二：数据采集与清洗 (ETL)
- 采集：将 NCDC 原始 `.gz` 压缩文件上传至 HDFS
- 清洗：编写 Java MapReduce 程序处理原始数据
- 技术挑战：处理了 22 年共 10,897 个小文件

#### 阶段三：数据仓库建设
- Hive 数仓分层：ODS → DIM → DWD → APP
- 使用 Sqoop 将分析结果导出至 MySQL

#### 阶段四：数据挖掘与预测
- 应用 Holt-Winters 和 ARIMA 模型预测气温
- 实现模型批量训练与自动化入库

### 常见故障排查

#### 基础设施与网络
1. **虚拟机网卡配置缺失**：添加 NAT 模式网卡
2. **Windows 无法访问 Hadoop Web**：修改 VMnet1 网段配置
3. **集群内网通信失败**：检查 `/etc/hosts` 配置

#### Hadoop 集群运维
4. **Slave 节点缺少环境**：使用 `scp` 分发 JDK/Hadoop
5. **Hive 连接拒绝**：重启后先执行 `start-all.sh`
6. **HDFS 安全模式**：执行 `hdfs dfsadmin -safemode leave`

#### MapReduce 开发
7. **OOM 内存溢出**：切换 YARN 模式 + 升级内存
8. **Active Nodes = 0**：补充 `yarn.resourcemanager.hostname` 配置
9. **ClassCastException**：避免使用 CombineTextInputFormat

#### Web 可视化
10. **np is not defined**：强制转换 numpy 类型为 Python 原生类型
11. **JS 中文乱码**：转换文件编码为 UTF-8
12. **MySQL 权限拒绝**：授予远程访问权限
13. **Django 版本不兼容**：使用 Django 3.2 LTS

### 常用命令速查
```bash
# 启动集群
sbin/start-dfs.sh
sbin/start-yarn.sh

# 退出安全模式
hdfs dfsadmin -safemode leave

# 查看节点状态
# HDFS: http://master:50070
# YARN: http://master:8088
```

</details>
