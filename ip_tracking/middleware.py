 from ipware import get_client_ip
 from .models import RequestLog

 class LogUserIpMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip, is_routable = get_client_ip(request)

        if client_ip is not None:
            request.user_ip = client_ip

            RequestLog.objects.create(
                ip_address=client_ip,
                path=request.path
            )

        response = self.get_response(request)
        return response