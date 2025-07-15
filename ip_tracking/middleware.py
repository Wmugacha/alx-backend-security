 from ipware import get_client_ip
 from .models import RequestLog, BlockedIP
 from django.http import HttpResponse
 from django_ip_geolocation.decorators import with_ip_geolocation
 from django.core.cache import cache


 class LogUserIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip, is_routable = get_client_ip(request)

        # Retrieve location from cache
        cache_key = f"geo:{client_ip}"
        location = cache.get(cache_key)

        if not location:
            request = with_ip_geolocation(lamda r: r)(request)
            location = getattr(request, 'geolocation', {})

            # Cache location
            cache.set(cache_key, location, timeout=3600)

        country = location.get('country', 'unknown')
        city = location.get('city', 'unkwown')

        if client_ip is not None:
            request.user_ip = client_ip

            if BlockedIP.objects.filter(ip_address=client_ip).exists():
                return HttpResponse("Access Denied: Your IP is blocked!!", status=403)

            request_log = RequestLog.objects.create(
                ip_address=client_ip,
                path=request.path,
                country=country,
                city=city
            )

        response = self.get_response(request)
        return response