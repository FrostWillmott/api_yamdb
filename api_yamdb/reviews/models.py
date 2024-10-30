from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models

ROLE_CHOICES = [
    ("user", "User"),
    ("moderator", "Moderator"),
    ("admin", "Admin"),
]

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    email = models.EmailField(
        max_length=254,
        validators=[MaxLengthValidator(254)],
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            MaxLengthValidator(150),
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message=r"Username must match the pattern: ^[\w.@+-]+\Z",
            ),
        ],
    )
    first_name = models.CharField(
        max_length=150,
        validators=[MaxLengthValidator(150)],
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        validators=[MaxLengthValidator(150)],
        blank=True,
    )

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator"
