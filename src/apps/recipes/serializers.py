from rest_framework import serializers

from .models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "title", "image_url", "description", "owner", "created_at", "updated_at"]
        read_only_fields = ["owner", "created_at", "updated_at"]
