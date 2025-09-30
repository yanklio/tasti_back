import requests
from django.core.management.base import BaseCommand
from django.conf import settings

from ...utils.bucket import get_presigned_url


class Command(BaseCommand):
    help = 'Test upload using presigned URL'

    def handle(self, *args, **options):
        # Generate a test presigned URL for image upload
        test_key = "test-image.png"
        try:
            url = get_presigned_url(test_key, "PUT")
            self.stdout.write(f"Generated presigned URL: {url}")

            # Use a small test image (minimal 1x1 PNG)
            # This is a minimal valid PNG file data
            test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

            # Upload using requests
            response = requests.put(
                url, 
                data=test_image_data, 
                headers={'Content-Type': 'image/png'}
            )

            self.stdout.write(f"Upload response status: {response.status_code}")
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("Image upload successful!"))
            else:
                self.stdout.write(self.style.ERROR(f"Upload failed: {response.text}"))

        except Exception as e:
            self.stderr.write(f"Error: {e}")