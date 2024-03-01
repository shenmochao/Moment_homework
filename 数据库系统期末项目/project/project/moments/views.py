from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.debug import sensitive_variables
from django.views.decorators.http import require_POST

from .models import WeChatUser, Status, Friendship, FriendshipRequest


# 主页
def home(request):
    return render(request, 'homepage.html')


# 展示用户资料
@login_required
def show_user(request):
    user = WeChatUser.objects.get(user=request.user)
    return render(request, 'user.html', {"user": user})


# 展示帖子
@login_required
def show_status(request):
    keyword = request.GET.get('keyword')
    if not keyword:
        statuses = Status.objects.all()
    else:
        # __contains 是一个过滤器，用于查找包含特定字符串的记录
        statuses = Status.objects.filter(Q(text__contains=keyword)
                                         | Q(user__user__username__contains=keyword))
    # 使用分页器 （变量， 展示几个）
    p = Paginator(statuses, 2)
    page = request.GET.get('page', 1)  # 若为空，置1
    statuses = p.page(page)
    return render(request, 'status.html', {
        'statuses': statuses,
        'keyword': keyword,
        'page': int(page),
        'page_range': p.page_range
    })


# 提交帖子
@login_required
def submit_post(request):
    user = WeChatUser.objects.get(user=request.user)
    text = request.POST.get('text')
    uploaded_file = request.FILES.get('pics')
    if uploaded_file:
        name = uploaded_file.name
        # 存储文件
        with open("./moments/static/image/{}".format(name), 'wb') as handle:
            for block in uploaded_file.chunks():
                handle.write(block)
    else:
        name = ''

    if text:
        status = Status(user=user, text=text, pics=name)
        status.save()
        return redirect('/status')

    return render(request, 'my_post.html')


# 展示好友请求
@login_required
def show_friends_requests(request):
    user = WeChatUser.objects.get(user=request.user)
    friend_requests_received = FriendshipRequest.objects.filter(to_user=user, pending='pending')

    # 构建好友请求信息列表，包括请求用户的信息、请求时间和请求ID
    requests_info = []
    for friendship_request in friend_requests_received:
        if hasattr(friendship_request, 'from_user') and hasattr(friendship_request.from_user,
                                                                'user') and friendship_request.from_user.user:
            requester_info = WeChatUser.objects.get(user=friendship_request.from_user.user)
            # 添加请求信息到字典中，包括请求用户的信息、请求时间和请求ID
            requests_info.append({'user': requester_info, 'request_date': friendship_request.request_date,
                                  'request_id': friendship_request.id})

    context = {"friend_requests": requests_info, "user": user}
    return render(request, 'friendsrequests.html', context)


# 展示朋友列表
@login_required
def friends(request):
    user = WeChatUser.objects.get(user=request.user)
    friends_list = Friendship.objects.filter(Q(user1=user) | Q(user2=user))

    # 构建好友信息列表，直接包含 WeChatUser 实例
    friends_info = []
    for friendship in friends_list:
        friend_user = friendship.user1 if friendship.user1 != user else friendship.user2
        friend_info = WeChatUser.objects.get(user=friend_user.user)
        friends_info.append(friend_info)

    return render(request, 'friends.html', {"friends_list": friends_info, "user": user})


# 用户注册
def register_user(request):
    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 设置默认的 first_name 和 last_name
        first_name = request.POST.get('first_name', 'DefaultFirstName')
        last_name = request.POST.get('last_name', 'DefaultLastName')

        # 创建 User
        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        # 处理密码
        user.set_password(password)
        user.save()

        # 对应到 WeChatUser
        WeChatUser.objects.create(user=user)
    except Exception as err:
        result = False
        message = str(err)
    else:
        result = True
        message = "Registration Successful"
    return JsonResponse({"result": result, "message": message})


# 好友请求处理
@require_POST
@login_required
def handle_friend_request(request):
    try:
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        # 获取好友请求对象
        friend_request = get_object_or_404(FriendshipRequest, id=request_id, to_user=request.user.wechatuser,
                                           pending='pending')

        # 处理好友请求
        with transaction.atomic():
            if action == 'accept':
                # 检查是否已经是好友
                if Friendship.objects.filter(user1=request.user.wechatuser,
                                             user2=friend_request.from_user).exists() or Friendship.objects.filter(
                        user1=friend_request.from_user, user2=request.user.wechatuser).exists():
                    # 已经是好友，返回消息
                    return JsonResponse({'message': '已经是好友'})

                # 添加好友关系
                Friendship.objects.create(user1=request.user.wechatuser, user2=friend_request.from_user)

            # 更新好友请求状态
            friend_request.pending = action
            friend_request.save()

        return JsonResponse({'message': '成功处理好友请求'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)


# 用户个人资料更新
@login_required
def update_user(request):
    try:
        pic = request.POST.get('pic')
        email = request.POST.get('email')
        region = request.POST.get('region')
        motto = request.POST.get('motto')
        if pic:
            WeChatUser.objects.filter(user=request.user).update(pic=pic)
        if region:
            WeChatUser.objects.filter(user=request.user).update(region=region)
        if motto:
            WeChatUser.objects.filter(user=request.user).update(motto=motto)
        if email:
            User.objects.filter(username=request.user).update(email=email)
    except Exception as err:
        result = False
        message = str(err)
    else:
        result = True
        message = "Update successfully!"
    return JsonResponse({"result": result, "message": message})


# 发送好友请求
@login_required
@require_POST
def send_friend_request(request, to_user_id):
    try:
        # 获取当前用户
        from_user = WeChatUser.objects.get(user=request.user)

        # 获取接收请求的用户
        to_user = WeChatUser.objects.get(id=to_user_id)

        # 检查是否尝试加自己为好友
        if from_user == to_user:
            return JsonResponse({'message': '跟自己做朋友吗，你一直都是哦！'})

        # 检查是否已经是好友
        if Friendship.objects.filter(Q(user1=from_user, user2=to_user) | Q(user1=to_user, user2=from_user)).exists():
            return JsonResponse({'message': '你们已经是好友了'})

        # 检查是否已经存在相同的好友请求
        existing_request = FriendshipRequest.objects.filter(from_user=from_user, to_user=to_user,
                                                            pending='pending').first()
        if existing_request:
            # 如果已经发送过好友请求，弹出消息告知
            return JsonResponse({'message': '你已经发送过好友请求了'})

        # 检查是否已经存在相同的反向好友请求（对方已经向当前用户发送过好友请求）
        reverse_request = FriendshipRequest.objects.filter(from_user=to_user, to_user=from_user,
                                                           pending='pending').first()
        if reverse_request:
            # 如果对方已经向你发送过好友请求，弹出消息并跳转到 /friendsrequests 的子页面
            return JsonResponse({'message': '对方已经向你发送过好友请求了', 'redirect': '../friendsrequests'})

        # 创建好友请求
        FriendshipRequest.objects.create(from_user=from_user, to_user=to_user, pending='pending')

        # 返回 JSON 响应，表示请求已发送
        return JsonResponse({'message': '好友请求发送成功'})
    except WeChatUser.DoesNotExist:
        return JsonResponse({'message': '错误：用户不存在'})
