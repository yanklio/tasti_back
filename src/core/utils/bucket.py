import logging
import os
import uuid

import boto3
from botocore.client import Config
from django.conf import settings

logger = logging.getLogger(__name__)

_bucket = None 


def get_bucket():
    global _bucket
    if _bucket is None:
        config = Config(
            signature_version="s3v4",
            s3={
                "addressing_style": "path"
            },
        )

        endpoint_url = getattr(settings, "AWS_S3_ENDPOINT_URL", None)

        _bucket = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=endpoint_url,
            config=config,
        )
    return _bucket


def get_presigned_url(key, method, expiration=3600):
    url_method = {"GET": "get_object", "PUT": "put_object", "DELETE": "delete_object"}.get(
        method.upper()
    )

    if not url_method:
        return None

    bucket = get_bucket()
    bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "default")

    try:
        url = bucket.generate_presigned_url(
            ClientMethod=url_method,
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise


def put_object(key, data, content_type=None):
    """Upload an object to the bucket"""
    bucket = get_bucket()
    bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "default")
    try:
        params = {"Bucket": bucket_name, "Key": key, "Body": data}
        if content_type:
            params["ContentType"] = content_type
        bucket.put_object(**params)
    except Exception as e:
        logger.error(f"Error uploading object {key}: {e}")
        raise

def generate_key(key, filename):
    name, ext = os.path.splitext(filename)
    clean_ext = ext.lstrip(".")
    return f"{key}/{uuid.uuid4()}.{clean_ext}"


def delete_object(key):
    """Delete an object from the bucket"""
    bucket = get_bucket()
    bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "default")
    try:
        bucket.delete_object(Bucket=bucket_name, Key=key)
    except Exception as e:
        logger.error(f"Error deleting object {key}: {e}")
        raise
