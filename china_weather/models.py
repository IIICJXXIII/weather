from django.db import models
from django.contrib.auth.models import User


class UserFavorite(models.Model):
    """用户收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    province = models.CharField(max_length=50, verbose_name='省份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    note = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        db_table = 'user_favorite'
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'province')  # 用户+省份唯一
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.province}'


class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    avatar = models.CharField(max_length=200, blank=True, default='', verbose_name='头像URL')
    location = models.CharField(max_length=50, blank=True, default='', verbose_name='所在地')
    bio = models.TextField(blank=True, default='', verbose_name='个人简介')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.user.username


class BrowseHistory(models.Model):
    """浏览历史"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    province = models.CharField(max_length=50, verbose_name='省份')
    visited_at = models.DateTimeField(auto_now=True, verbose_name='访问时间')
    
    class Meta:
        db_table = 'browse_history'
        verbose_name = '浏览历史'
        verbose_name_plural = verbose_name
        ordering = ['-visited_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.province}'

