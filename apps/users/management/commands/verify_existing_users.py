from django.core.management.base import BaseCommand
from apps.users.models import Profile


class Command(BaseCommand):
    help = "Mark all existing user profiles as email verified (for pre-existing users)."

    def handle(self, *args, **options):
        updated = Profile.objects.filter(email_verified=False).update(email_verified=True)
        self.stdout.write(self.style.SUCCESS(f"Marked {updated} profile(s) as email verified."))

