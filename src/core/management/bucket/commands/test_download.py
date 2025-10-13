import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from core.utils.bucket import get_presigned_url


class Command(BaseCommand):
    help = 'Test download using presigned URL'

    def handle(self, *args, **options):
        # Test downloading the uploaded image
        test_key = "test-image.png"
        try:
            url = get_presigned_url(test_key, "GET")
            self.stdout.write(f"Generated download URL: {url}")

            # Download using requests
            response = requests.get(url)

            self.stdout.write(f"Download response status: {response.status_code}")
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS(f"Download successful! Content length: {len(response.content)} bytes"))
                # Check if it's PNG content
                if response.content.startswith(b'\x89PNG'):
                    self.stdout.write(self.style.SUCCESS("Content appears to be valid PNG"))
                else:
                    self.stdout.write(self.style.WARNING("Content may not be valid PNG"))
            else:
                self.stdout.write(self.style.ERROR(f"Download failed: {response.text}"))

        except Exception as e:
            self.stderr.write(f"Error: {e}")