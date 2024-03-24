import re

from django.core.exceptions import ValidationError
from django.utils import timezone

BANNED_USERNAME = ('me',)


def validate_username(username):
    if username.lower() in BANNED_USERNAME:
        raise ValidationError(f'Недопустимое имя пользователя: "{username}".')
    if not re.match(r'^[\w.@+-]+$', username):
        invalid_chars = ''.join(
            char for char in username if not re.match(r'[\w.@+-]', char))
        raise ValidationError(f'Недопустимые символы: {invalid_chars}')
    return username


def validate_year(year):
    current_year = timezone.now().year
    if year > current_year:
        raise ValidationError(
            f'Указанный год {year} не можеть быть '
            f'больше текущего {current_year}')
    return year
