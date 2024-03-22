from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'bio',
        'email',
        'role',
    )
    search_fields = ('username', 'email')
    list_editable = ('role',)
    list_filter = ('username',)
    empty_value_display = 'значение отсутствует'
