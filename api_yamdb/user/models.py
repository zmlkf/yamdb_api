from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import ADMIN, USER, MODERATOR, ROLE_CHOICES
from .validators import username_validator


class CustomUser(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        null=False,
        unique=True,
        validators=(username_validator, AbstractUser.username_validator),
        blank=False,
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=256,
        choices=ROLE_CHOICES,
        default=USER
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (
            self.role == ADMIN
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self) -> str:
        return self.username
