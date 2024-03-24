from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор')
)

TEXT_LENGTH = 50


class User(AbstractUser):
    """
    Пользователь системы.

    Расширяет стандартную модель пользователя Django.

    Поля:
    - username: Имя пользователя
    - email: Электронная почта
    - bio: Биография
    - role: Роль пользователя (админ, модератор или обычный пользователь)

    Методы:
    - is_admin: Проверка, является ли пользователь администратором
    - is_moderator: Проверка, является ли пользователь модератором
    """
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=(username_validator, AbstractUser.username_validator),
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=256,
        choices=ROLE_CHOICES,
        default=USER
    )

    class Meta:
        unique_together = ('username', 'email')
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_superuser
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self) -> str:
        return self.username[:TEXT_LENGTH]
