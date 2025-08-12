from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from OHC_System.models import Profile

class Command(BaseCommand):
    help = 'Creates missing user profiles'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0

        for user in users:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(users)} users. Created {created_count} missing profiles.'
            )
        )
