from django.contrib import admin

from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "image_url", "description", "owner", "created_at", "updated_at"]
    list_filter = ["title"]
    search_fields = ["title", "description"]
    ordering = ["id"]
