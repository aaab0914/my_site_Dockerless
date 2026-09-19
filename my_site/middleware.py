from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Require unauthenticated users to stay on public pages.
    Redirect all other requests to the login page.
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
