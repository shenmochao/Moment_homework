from django.contrib import admin
from moments.models import WeChatUser, Status, FriendshipRequest, Friendship


# 这个类可以用于管理后端的管理员界面
class StatusAdmin(admin.ModelAdmin):
    list_display = ["user", "text", "pics", "pub_time"]
    # 对于Status中的user变量，他是WeChatUser的外键，可以通过调用User类来获取属性username
    search_fields = ["user__user__username", "text", "pics"]
    # 按照发布时间
    date_hierarchy = "pub_time"
    #
    list_filter = ["user__user__username", "text"]


admin.site.register(WeChatUser)
admin.site.register(Status, StatusAdmin)


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ["id", "user1", "user2", "friendship_date"]
    search_fields = ["user1__user__username", "user2__user__username"]
    date_hierarchy = "friendship_date"
    list_filter = ["user1__user__username", "user2__user__username"]


admin.site.register(Friendship, FriendshipAdmin)


class FriendshipRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "from_user", "to_user", "pending", "request_date"]
    search_fields = ["from_user__user__username", "to_user__user__username"]
    date_hierarchy = "request_date"
    list_filter = ["from_user__user__username", "to_user__user__username", "pending"]


admin.site.register(FriendshipRequest, FriendshipRequestAdmin)
