from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Assign users to Admin or Normal User groups based on is_staff flag'

    def handle(self, *args, **options):
        User = get_user_model()

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        user_group, _ = Group.objects.get_or_create(name='Normal User')

        users = User.objects.all()
        admin_count = 0
        user_count = 0

        for user in users:
            user.groups.clear()  # Optional: remove old group assignments

            if user.is_staff or user.is_superuser:
                user.groups.add(admin_group)
                admin_count += 1
            else:
                user.groups.add(user_group)
                user_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Assigned {admin_count} Admins and {user_count} Normal Users."
        ))
