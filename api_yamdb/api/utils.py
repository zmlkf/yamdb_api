from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from api_yamdb.settings import EMAIL_ADMIN


def send_confirmation_code(user):

    send_mail(
        'Код для получения токена к API',
        f'Код подтверждения {default_token_generator.make_token(user)}',
        f'{EMAIL_ADMIN}',
        [user.email],
    )
