import re

from django.core.exceptions import ValidationError
from django.utils import timezone

from api_yamdb.settings import ME_URL

BANNED_USERNAME = (ME_URL,)


def validate_username(username):
    if username in BANNED_USERNAME:
        raise ValidationError(f'Недопустимое имя пользователя: "{username}".')
    invalid_chars = re.sub(r'[\w.@+-]', '', username)
    if invalid_chars:
        raise ValidationError(f'Недопустимые символы: {invalid_chars}')
    return username


def validate_year(year):
    current_year = timezone.now().year
    if year > current_year:
        raise ValidationError(
            f'Указанный год {year} не можеть быть '
            f'больше текущего {current_year}')
    return year
