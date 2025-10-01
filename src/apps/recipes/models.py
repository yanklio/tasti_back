from django.conf import settings
from django.db import models

from core.utils.bucket import delete_object


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recipes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # S3 storage fields
    image_bucket_key = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.owner.username}"

    def update_image(self, s3_key):
        """Update the S3 image key, deleting the old one if different"""
        if self.image_bucket_key and self.image_bucket_key != s3_key:
            try:
                delete_object(self.image_bucket_key)
            except Exception:
                pass 
        self.image_bucket_key = s3_key
        self.save(update_fields=["image_bucket_key", "updated_at"])

    def clear_image(self):
        """Clear the S3 image key, deleting the old one"""
        if self.image_bucket_key:
            try:
                delete_object(self.image_bucket_key)
            except Exception:
                pass  
        self.image_bucket_key = None
        self.save(update_fields=["image_bucket_key", "updated_at"])

    @property
    def has_image(self):
        """Check if recipe has an image"""
        return bool(self.image_bucket_key)
