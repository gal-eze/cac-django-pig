from django.contrib.auth.models import AbstractUser


class AppUser(AbstractUser):
    pass

    def __str__(self):
        return self.username
