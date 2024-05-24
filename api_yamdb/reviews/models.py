from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (ADMIN, MAX_LENGTH_EMAIL, MAX_LENGTH_NAME,
                        MAX_LENGTH_SLUG, MAX_LENGTH_USERNAME, MAX_SCORE,
                        MIN_SCORE, MODERATOR, ROLE_CHOICES, TEXT_LENGTH, USER)
from .validators import validate_username, validate_year


class User(AbstractUser):
    """
    User of the system.

    Extends Django's default user model.

    Fields:
    - username: User's username
    - email: Email address
    - bio: Biography
    - role: User's role (admin, moderator, or regular user)

    Methods:
    - is_admin: Checks if the user is an administrator
    - is_moderator: Checks if the user is a moderator
    """
    username = models.CharField(
        'Username',
        max_length=MAX_LENGTH_USERNAME,
        help_text=(f'No more than {MAX_LENGTH_USERNAME} characters. '
                   f'Letters, numbers, and @/./+/-/'),
        unique=True,
        validators=(validate_username,),
    )
    email = models.EmailField(
        'Email',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    bio = models.TextField(
        'Biography',
        blank=True,
    )
    role = models.CharField(
        'Role',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'), name='unique_user'),
        )

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self) -> str:
        return self.username[:TEXT_LENGTH]


class NamedEntity(models.Model):
    """
    Abstract class for named models.

    Fields:
    - name: Name
    - slug: Slug
    """

    name = models.CharField(
        'Name', max_length=MAX_LENGTH_NAME)
    slug = models.SlugField(
        'Slug', unique=True, max_length=MAX_LENGTH_SLUG)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class Genre(NamedEntity):
    """
    Model for genres of works.

    Inherits from the abstract class NamedEntity.
    """

    class Meta(NamedEntity.Meta):
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'


class Category(NamedEntity):
    """
    Model for categories of works.

    Inherits from the abstract class NamedEntity.
    """

    class Meta(NamedEntity.Meta):
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Title(models.Model):
    """
    Model for works.

    Fields:
    - name: Name
    - year: Publication year
    - description: Description
    - genre: Genres
    - category: Category
    """
    name = models.CharField('Name', max_length=MAX_LENGTH_NAME)
    year = models.SmallIntegerField(
        'Publication year', validators=(validate_year,))
    description = models.TextField('Description', blank=True, null=True)
    genre = models.ManyToManyField(Genre, verbose_name='Genre')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name='Category',
        null=True
    )

    class Meta:
        default_related_name = 'titles'
        verbose_name = 'Work'
        verbose_name_plural = 'Works'
        ordering = ('name',)

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class TextContent(models.Model):
    """
    Abstract class for text-based models.

    Fields:
    - text: Text
    - author: Text's author
    - pub_date: Publication date
    """

    text = models.TextField(verbose_name='Text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    class Meta:
        abstract = True
        default_related_name = "%(class)ss"
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:TEXT_LENGTH]


class Review(TextContent):
    """
    Model for reviews of works.
    Inherits from the abstract class

    Fields:
    - title: Work
    - score: Score
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Work'
    )
    score = models.SmallIntegerField(
        verbose_name='Score',
        validators=(MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE))
    )

    class Meta(TextContent.Meta):
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'),
        )


class Comment(TextContent):
    """
    Model representing comments on reviews of works.
    Inherits from the abstract class

    Fields:
    - review: Review of the work
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Review of the work'
    )

    class Meta(TextContent.Meta):
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
