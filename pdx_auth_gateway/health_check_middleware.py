# ref: https://stackoverflow.com/questions/32920688/how-to-setup-health-check-page-in-django
from django.http import HttpResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthcheck":
            return HttpResponse("ok")
        return self.get_response(request)
