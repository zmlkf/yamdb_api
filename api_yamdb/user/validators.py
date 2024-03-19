from django.core.exceptions import ValidationError

from .constants import BANNED_USERNAME


def username_validator(username):
    if username in BANNED_USERNAME:
        raise ValidationError(f'Имя пользователя не может быть {username}')
    return username
