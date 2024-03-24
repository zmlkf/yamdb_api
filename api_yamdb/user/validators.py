from django.core.exceptions import ValidationError

BANNED_USERNAME = ('me',)


def username_validator(username):
    if username in BANNED_USERNAME:
        raise ValidationError(f'Имя пользователя не может быть {username}')
    return username
