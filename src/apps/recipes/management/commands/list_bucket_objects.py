from django.core.management.base import BaseCommand
from django.conf import settings

from ...utils.bucket import get_bucket


class Command(BaseCommand):
    help = 'List objects in the S3 bucket'

    def handle(self, *args, **options):
        bucket = get_bucket()
        bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "default")

        self.stdout.write(f"Listing objects in bucket: {bucket_name}")

        try:
            response = bucket.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                for obj in response['Contents']:
                    self.stdout.write(f"  {obj['Key']} - {obj['Size']} bytes - {obj['LastModified']}")
            else:
                self.stdout.write("No objects found in bucket")
        except Exception as e:
            self.stderr.write(f"Error listing objects: {e}")