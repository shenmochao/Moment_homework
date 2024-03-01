from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from moments.views import home, show_user, show_status, submit_post, friends, register_user, update_user, \
    show_friends_requests, handle_friend_request, send_friend_request

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='homepage.html')),
    path('user', show_user),
    path('status', show_status),
    path('post', submit_post),
    path('exit', LogoutView.as_view(next_page='/')),
    path('friends', friends),
    path('register_user', register_user),
    path('update_user', update_user),
    path('friendsrequests', show_friends_requests),
    path('handle_friend_request', handle_friend_request, name='handle_friend_request'),
    path('send_friend_request/<int:to_user_id>/', send_friend_request, name='send_friend_request'),
]
