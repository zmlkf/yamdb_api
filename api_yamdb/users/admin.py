# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'role',
    )
    search_fields = ('username', 'email')
    list_editable = ('role',)
    list_filter = ('username',)
