from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.db import models


class CategoryGenreAbstract(models.Model):
    name = models.CharField(
        'Название', max_length=256
    )
    slug = models.SlugField(
        'Слаг', unique=True, max_length=50
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:50]


class Genre(CategoryGenreAbstract):

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Comment(models.Model):
    pass


class Review(models.Model):
    pass


class Category(models.Model):
    name = models.CharField(
        'Наименование', max_length=256
    )
    slug = models.SlugField(
        'Слаг', unique=True, max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)


class Title(models.Model):
    name = models.CharField('Наименование', max_length=256)
    year = models.IntegerField(
        'Год публикации',
        validators=[
            MinValueValidator(1700), MaxValueValidator(timezone.now().year)]
    )
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
        return self.name[:50]
