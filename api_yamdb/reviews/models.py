from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_username, validate_year

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор')
)

TEXT_LENGTH = 50
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_ROLE = max(len(role[0]) for role in ROLE_CHOICES)
MAX_LENGTH_NAME = 256
MAX_LENGTH_SLUG = 50
MIN_SCORE = 1
MAX_SCORE = 10


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
        max_length=MAX_LENGTH_USERNAME,
        help_text='Не более 150 символов. Буквы, цифры и @/./+/-/',
        unique=True,
        validators=(validate_username,),
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH_ROLE,
        choices=ROLE_CHOICES,
        default=USER
    )

    class Meta:
        unique_together = ('username', 'email')
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self) -> str:
        return self.username[:TEXT_LENGTH]


class CategoryGenreAbstract(models.Model):
    """
    Абстрактный класс для жанров и категорий.

    Поля:
    - name: Название
    - slug: Слаг
    """

    name = models.CharField(
        'Название', max_length=MAX_LENGTH_NAME)
    slug = models.SlugField(
        'Слаг', unique=True, max_length=MAX_LENGTH_SLUG)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class Genre(CategoryGenreAbstract):
    """
    Модель для жанров произведений.

    Наследуется от абстрактного класса CategoryGenreAbstract.
    """

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(CategoryGenreAbstract):
    """
    Модель для категорий произведений.

    Наследуется от абстрактного класса CategoryGenreAbstract.
    """

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """
    Модель для произведений.

    Поля:
    - name: Наименование
    - year: Год публикации
    - description: Описание
    - genre: Жанры
    - category: Категория
    """
    name = models.CharField('Наименование', max_length=MAX_LENGTH_NAME)
    year = models.SmallIntegerField(
        'Год публикации', validators=(validate_year,))
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанры')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        null=True
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class ReviewCommentAbstract(models.Model):
    """
    Абстрактный класс для отзывов и комментариев.

    Поля:
    - text: Текс
    - author: Автор текста
    - pub_date: Дата публикации
    """

    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:TEXT_LENGTH]


class Review(ReviewCommentAbstract):
    """
    Модель для отзывов к произведениям.
    Унаследована от абстрактного класса

    Поля:
    - title: Произведение
    - score: Оценка
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE))
    )

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'),
        )


class Comment(ReviewCommentAbstract):
    """
    Модель для представления комментариев к отзывам о произведениях.
    Унаследована от абстрактного класса

    Поля:
    - review: Отзыв к произведению
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв к произведению'
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
