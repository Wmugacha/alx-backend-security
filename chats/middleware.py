import logging
from datetime import datetime, time
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
from django.urls import reverse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, get_response):

        self.get_response = get_response

        logger.info("Request logging initialized")
    
    def __call__(self, request):

        response = self.get_response(request)

        user = getattr(request, 'user', 'Anonymous')
        if user != 'Anonymous' and user.is_authenticated:
            user = str(user)
        else:
            user = 'Anonymous'
        logger.info(f"{timezone.now()} - User: {user} - Path: {request.path}")

        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.start_time = time(18, 0)
        self.end_time = time(21, 0)

        logger.info(f"Time based access is in place: {self.start_time} to {self.end_time}")

    def is_time_allowed(self, current_time):
        return self.start_time <= current_time <= self.end_time

    def __call__(self, request):
        current_time = timezone.now().time()

        if not self.is_time_allowed(current_time):
            logger.warning(f"Access denied at {current_time} - Outside allowed hours")
            return HttpResponseForbidden("Access denied: Outside allowed timeframe")
        else:
            logger.debug(f"Granted access at: {current_time}")
            return self.get_response(request)


class OffensiveLanguageMiddleware:
    RATE_LIMIT = 5
    WINDOW_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/messages"):

            ip = self.get_client_ip(request)

            key = f"msg-rate-{ip}"

            request_times = cache.get(key, [])

            now = time.time()

            request_times = [t for t in request_times if now - t < self.WINDOW_SECONDS]

            if len(request_times) >= self.RATE_LIMIT:
                return JsonResponse(
                    {"detail": "Rate limit exceed. 5 messages allowed per minute"},
                    status=429
                )
            request_times.append(now)

            cache.set(key, request_times, timeout=self.WINDOW_SECONDS)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwaded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwaded_for:
            return x_forwaded_for.split(',')[0].strip()

        return request.META.get('REMOTE_ADDR')


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.exempt_paths = [
            "/admin/login/",
            "/admin/logout/",
            "/admin/", 
            "/accounts/login/",
        ]
    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.exempt_paths):
            return self.get_response(request)

        if (
            not request.user.is_authenticated or 
            not (
                request.user.groups.filter(name="Admin").exists() or
                request.user.groups.filter(name="Moderator").exists()
            )
        ):
            return HttpResponseForbidden("Only Admin or Moderator Level Access Allowed")

        logger.info("User role is granted access")
        return self.get_response(request)
