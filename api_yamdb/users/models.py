from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import MAX_LENGHT_FIELD, TEXT_LENGTH


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'
    ROLE_CHOICES = (
        (USER_ROLE, 'Пользователь'),
        (MODERATOR_ROLE, 'Модератор'),
        (ADMIN_ROLE, 'Администратор')
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGHT_FIELD,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message=('Имя пользователя содержит недопустимый символ'),
            )
        ],
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGHT_FIELD,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGHT_FIELD,
        blank=True
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGHT_FIELD,
        unique=True
    )
    role = models.CharField(
        'Пользовательская роль',
        choices=ROLE_CHOICES,
        default=USER_ROLE,
        max_length=MAX_LENGHT_FIELD,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username[:TEXT_LENGTH]

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR_ROLE

    @property
    def is_admin(self):
        return (
            self.role == User.ADMIN_ROLE
            or self.is_staff
            or self.is_superuser
        )
