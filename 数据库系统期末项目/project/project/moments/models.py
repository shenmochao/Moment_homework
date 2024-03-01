from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class WeChatUser(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    motto = models.CharField(max_length=100, null=True, blank=True)
    pic = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Status(models.Model):
    user = models.ForeignKey(WeChatUser, models.CASCADE)
    text = models.CharField(max_length=280)
    pics = models.CharField(max_length=100, null=True, blank=True)
    pub_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-id']


# 用于记录朋友关系
class Friendship(models.Model):
    user1 = models.ForeignKey(WeChatUser, related_name='user1_friends', on_delete=models.CASCADE)
    user2 = models.ForeignKey(WeChatUser, related_name='user2_friends', on_delete=models.CASCADE)
    friendship_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user1.user.username} - {self.user2.user.username}'

    class Meta:
        unique_together = ['user1', 'user2']


# 用于记录好友请求
class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(WeChatUser, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(WeChatUser, related_name='friendship_requests_received', on_delete=models.CASCADE)
    pending = models.CharField(max_length=15, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
