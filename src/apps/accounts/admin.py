from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
    ]


admin.site.register(User, CustomUserAdmin)
