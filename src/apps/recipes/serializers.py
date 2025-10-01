from rest_framework import serializers

from .models import Recipe
from .utils.bucket import get_presigned_url


class RecipeSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    image_download_url = serializers.SerializerMethodField(read_only=True)
    request_presigned_url = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "image_bucket_key",
            "image_download_url",
            "description",
            "owner",
            "created_at",
            "updated_at",
            "request_presigned_url",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def validate_image_bucket_key(self, value):
        if value and not isinstance(value, str):
            raise serializers.ValidationError("Image bucket key must be a string.")
        return value

    def get_image_download_url(self, obj):
        """Generate presigned download URL if image exists"""
        if obj.has_image:
            try:
                return get_presigned_url(obj.image_bucket_key, "GET", expiration=3600)
            except Exception:
                return None
        return None
