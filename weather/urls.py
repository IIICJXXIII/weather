"""weather URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from china_weather import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # 首页
    path('', views.login, name='home'),
    path('map_sample/', views.map_sample),
    # 省份相关
    path('province/', views.province_list, name='province_list'),
    path('province/<str:province_name>/', views.province_detail, name='province_detail'),
    # 历史查询
    path('history/', views.history_query, name='history_query'),
    # 数据对比
    path('compare/', views.compare, name='compare'),
    # 数据分析
    path('analysis/', views.analysis, name='analysis'),
    # 关于项目
    path('about/', views.about, name='about'),
    
    # 用户系统
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('settings/', views.user_settings, name='user_settings'),
    
    # 收藏 API
    path('api/favorite/add/', views.add_favorite, name='add_favorite'),
    path('api/favorite/remove/', views.remove_favorite, name='remove_favorite'),
    path('api/favorite/check/', views.check_favorite, name='check_favorite'),
    path('api/toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    # 清空操作
    path('clear-history/', views.clear_history, name='clear_history'),
    path('clear-favorites/', views.clear_favorites, name='clear_favorites'),
]