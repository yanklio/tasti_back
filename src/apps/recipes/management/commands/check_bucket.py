from django.core.management.base import BaseCommand
from django.conf import settings

from ...utils.bucket import get_bucket


class Command(BaseCommand):
    help = 'Check if the S3 bucket exists'

    def handle(self, *args, **options):
        bucket = get_bucket()
        bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "default")

        self.stdout.write(f"Checking bucket: {bucket_name}")

        try:
            response = bucket.head_bucket(Bucket=bucket_name)
            self.stdout.write(self.style.SUCCESS(f"Bucket '{bucket_name}' exists"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Bucket '{bucket_name}' does not exist or error: {e}"))