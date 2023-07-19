from django.contrib.auth.models import User

from users.models import Profile


def run():
    users = User.objects.all()
    for user in users:
        profile, created = Profile.objects.get_or_create(
            user=user
        )
