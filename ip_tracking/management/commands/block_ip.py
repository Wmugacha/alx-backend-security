from django.core.management.base import BaseCommand, commandError
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Add an ip address to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='The ip address to block')
        parser.add_argument('--path', type=str, default='/' help='The path the ip is trying to access')

    def handle(self, *args, **options):
        ip = options['ip_address']
        path = options['path']

        if BlockedIP.objects.filter(ip_address=ip).exists():
            self.stdout.write(self.style.WARNING(f"IP {ip} is already blocked."))
            return
        
        BlockedIP.objects.create(ip_address=ip, path=path)
        self.stdout.write(self.style.SUCCESS(f"Successfully blocked IP: {ip} on path: {path}"))     