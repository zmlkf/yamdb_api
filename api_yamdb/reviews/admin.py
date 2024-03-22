from django.contrib import admin
from django.contrib.auth import get_user_model

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title

User = get_user_model()

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка административного интерфейса для пользователей."""
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'bio', 'role')
    list_editable = ('role',)
    search_fields = ('role', 'username')
    list_filter = ('role', 'username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки административного интерфейса для категорий."""
    list_display = ('pk', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Настройки административного интерфейса для жанров."""
    list_display = ('pk', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Настройки административного интерфейса для произведений."""
    list_display = ('pk', 'name', 'year', 'description', 'category')
    list_filter = ('name',)
    search_fields = ('name', 'year', 'category')


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    """Настройки административного интерфейса
    для соответствия жанров и произведений.
    """
    list_display = ('pk', 'genre', 'title')
    list_filter = ('genre',)
    search_fields = ('title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Настройки административного интерфейса для отзывов."""
    list_display = ('pk', 'title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('title', 'text')
    list_filter = ('pub_date', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройки административного интерфейса для комментариев."""
    list_display = ('pk', 'review', 'text', 'author', 'pub_date')
    search_fields = ('review', 'text')
    list_filter = ('pub_date', 'author')