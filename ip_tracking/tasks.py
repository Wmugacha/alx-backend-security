from django.conf import settings
import logging
from messaging_app.celery import app
from django_ratelimit.core import is_ratelimited
from .models import SuspiciousIP, RequestLog
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)
def flag_suspicious_ips():
    one_hour_ago = timezone.now() - timedelta(hours=1)

    sus_ips = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago
    ).values('ip_address').annotate(
        request_count=Count('ip_address')
    ).filter(
        request_count__gt=100
    )

    for sus_ip in sus_ips:
        ip = sus_ip['ip_address']
        count = sus_ip['request_count']
        reason = f"Exceeded 100 requests ({count}) in the last hour."

        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address = ip,
            defaults={'reason': reason}
        )

        if not created:
            if reason not in suspicious_ip.reason:
                suspicious_ip.reason += f"\n- {reason}"
                suspicious_ip.save()

    sensitive_paths = ['/admin', '/login/']
    sensitive_access_ips = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path=sensitive_paths
    ).values('ip_address').distinct()

    for sus_ip in sensitive_access_ips:
        ip = sus_ip['ip_address']

        # Find the specific paths accessed by this IP
        accessed_paths = RequestLog.objects.filter(
            ip_address=ip,
            timestamp__gte=one_hour_ago,
            path__in=sensitive_paths
        ).values_list('path', flat=True).distinct()
        
        reason = f"Accessed sensitive path(s) in the last hour: {', '.join(accessed_paths)}."

        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            defaults={'reason': reason}
        )
        if not created:
            if reason not in suspicious_ip.reason:
                suspicious_ip.reason += f"\n- {reason}"
                suspicious_ip.save()
