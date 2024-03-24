from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator

TEXT_LENGTH = 50
User = get_user_model()


class CategoryGenreAbstract(models.Model):
    """
    Абстрактный класс для жанров и категорий.

    Поля:
    - name: Название
    - slug: Слаг
    """

    name = models.CharField(
        'Название', max_length=256)
    slug = models.SlugField(
        'Слаг', unique=True, max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class Genre(CategoryGenreAbstract):
    """
    Модель для жанров произведений.

    Наследуется от абстрактного класса CategoryGenreAbstract.
    """

    class Meta:
        ordering = ('name',)
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(CategoryGenreAbstract):
    """
    Модель для категорий произведений.

    Наследуется от абстрактного класса CategoryGenreAbstract.
    """

    class Meta:
        ordering = ('name',)
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
    name = models.CharField('Наименование', max_length=256)
    year = models.SmallIntegerField(
        'Год публикации', validators=(year_validator,))
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


class Review(models.Model):
    """
    Модель для отзывов к произведениям.

    Поля:
    - title: Произведение
    - text: Текст отзыва
    - author: Автор
    - score: Оценка
    - pub_date: Дата публикации
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        validators=(MinValueValidator(1), MaxValueValidator(10))
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('title', 'author')

    def __str__(self):
        return self.text[:TEXT_LENGTH]


class Comment(models.Model):
    """
    Модель для представления комментариев к отзывам о произведениях.

    Поля:
    - review: Отзыв к произведению
    - text: Комментарий
    - author: Автор
    - pub_date: Дата публикации
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв к произведению'
    )
    text = models.TextField(verbose_name='Комментарий')
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
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TEXT_LENGTH]
