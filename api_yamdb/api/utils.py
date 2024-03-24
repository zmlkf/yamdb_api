from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from api_yamdb.settings import EMAIL_ADMIN

User = get_user_model()


def send_confirmation_code(request):

    user = get_object_or_404(
        User, username=request.data.get('username'),)
    send_mail(
        'Код для получения токена к API',
        f'Код подтверждения {default_token_generator.make_token(user)}',
        f'{EMAIL_ADMIN}',
        [request.data.get('email')],
    )
