from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'
    ROLE_CHOICES = (
        (USER_ROLE, 'Пользователь'),
        (MODERATOR_ROLE, 'Модератор'),
        (ADMIN_ROLE, 'Администратор')
    )
    username = models.CharField('Username', max_length=50, unique=True)
    email = models.EmailField('Электронная почта', max_length=50, unique=True)
    confirmation_code = models.CharField('Код подтверждения', max_length=6)
    role = models.CharField(
        'Пользовательская роль',
        choices=ROLE_CHOICES,
        default=USER_ROLE,
        max_length=50,
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == User.USER_ROLE

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR_ROLE

    @property
    def is_admin(self):
        return (
            self.role == User.ADMIN_ROLE
            or self.is_staff
            or self.is_superuser
        )
