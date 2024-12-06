from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class AllowIframeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith(settings.MEDIA_URL):
            response["X-Frame-Options"] = "ALLOWALL"
        return response
