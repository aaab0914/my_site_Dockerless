from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    中间件：强制未登录用户只能访问首页、登录和注册页面。
    访问其他任何页面都跳转到登录页面。
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = [
            '/blog/',
            '/users/login/',
            '/users/register/',
        ]

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        if request.path in self.allowed_paths:
            return self.get_response(request)

        return redirect(reverse('users:login'))
