from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserFavorite, UserProfile, BrowseHistory


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """用户收藏管理"""
    list_display = ['user', 'province', 'created_at', 'note']
    list_filter = ['province', 'created_at']
    search_fields = ['user__username', 'province', 'note']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """用户信息管理"""
    list_display = ['user', 'location', 'created_at']
    list_filter = ['location', 'created_at']
    search_fields = ['user__username', 'location', 'bio']
    ordering = ['-created_at']


@admin.register(BrowseHistory)
class BrowseHistoryAdmin(admin.ModelAdmin):
    """浏览历史管理"""
    list_display = ['user', 'province', 'visited_at']
    list_filter = ['province', 'visited_at']
    search_fields = ['user__username', 'province']
    ordering = ['-visited_at']
    date_hierarchy = 'visited_at'


# 扩展 User 管理，显示关联的 Profile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户扩展信息'


class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'is_staff', 'date_joined']


# 重新注册 User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 自定义管理后台标题
admin.site.site_header = '中国天气可视化系统 - 管理后台'
admin.site.site_title = '天气系统管理'
admin.site.index_title = '欢迎使用管理后台'
