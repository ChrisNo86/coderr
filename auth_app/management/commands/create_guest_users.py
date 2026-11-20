"""Management command that creates the guest accounts of the frontend."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from profile_app.models import UserProfile

GUEST_USERS = [
    {"username": "andrey", "password": "asdasd", "type": "customer"},
    {"username": "kevin", "password": "asdasd24", "type": "business"},
]


class Command(BaseCommand):
    """Create the customer and business guest users if missing."""

    help = "Creates the guest users used by the frontend guest logins."

    def handle(self, *args, **options):
        """Create every guest user that does not exist yet."""
        for guest in GUEST_USERS:
            if User.objects.filter(username=guest["username"]).exists():
                self.stdout.write(f"{guest['username']} already exists.")
                continue
            self.create_guest(guest)
            self.stdout.write(
                self.style.SUCCESS(f"{guest['username']} created.")
            )

    def create_guest(self, guest):
        """Create one guest user together with the profile."""
        user = User.objects.create_user(
            username=guest["username"],
            email=f"{guest['username']}@guest.coderr",
            password=guest["password"],
        )
        UserProfile.objects.create(user=user, type=guest["type"])
