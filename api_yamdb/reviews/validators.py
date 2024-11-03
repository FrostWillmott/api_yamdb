from django.utils import timezone
from rest_framework.exceptions import ValidationError


def me_username_validator(username):
    if username == "me":
        raise ValidationError("Username 'me' is not allowed.")


def validate_year(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(f"Год не может быть больше чем {current_year}.")