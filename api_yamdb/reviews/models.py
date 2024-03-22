from django.db import models

from .validators import year_validator
TEXT_LENGTH = 50


class CategoryGenreAbstract(models.Model):
    """
    Абстрактный класс для жанров и категорий.

    Поля:
    - name: Название
    - slug: Слаг
    """

    name = models.CharField(
        'Название', max_length=256
    )
    slug = models.SlugField(
        'Слаг', unique=True, max_length=50
    )

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
    genre = models.ManyToManyField(
        Genre, verbose_name='Жанры'
    )
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
