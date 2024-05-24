from django.contrib import admin
from django.contrib.auth import get_user_model

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()

admin.site.empty_value_display = 'Not set'


class TitleGenreInline(admin.TabularInline):
    """Inline class for displaying related objects Genre and Title."""
    model = Title.genre.through
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface setup for users."""
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'bio', 'role')
    list_editable = ('role',)
    search_fields = ('role', 'username')
    list_filter = ('role', 'username')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface setup for categories."""
    list_display = ('pk', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin interface setup for genres."""
    inlines = [TitleGenreInline]
    list_display = ('pk', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Admin interface setup for titles."""
    inlines = [TitleGenreInline]
    list_display = ('pk', 'name', 'year', 'description', 'category')
    list_filter = ('name',)
    search_fields = ('name', 'year', 'category')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface setup for reviews."""
    list_display = ('pk', 'title', 'text', 'author', 'score', 'pub_date')
    search_fields = ('title', 'text')
    list_filter = ('pub_date', 'author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface setup for comments."""
    list_display = ('pk', 'review', 'text', 'author', 'pub_date')
    search_fields = ('review', 'text')
    list_filter = ('pub_date', 'author')
