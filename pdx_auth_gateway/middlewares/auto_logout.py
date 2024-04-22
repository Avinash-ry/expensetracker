import time
from django.contrib.auth import logout


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            last_login_time = request.user.last_login.timestamp()

            timeout_duration = 500  # in seconds

            if time.time() - last_login_time > timeout_duration:
                logout(request)

        return response
