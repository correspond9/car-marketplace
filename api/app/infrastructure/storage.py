import uuid
from functools import lru_cache

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


class StorageError(Exception):
    def __init__(self, message: str, code: str = "STORAGE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class StorageService:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            kwargs: dict = {
                "service_name": "s3",
                "aws_access_key_id": settings.s3_access_key or None,
                "aws_secret_access_key": settings.s3_secret_key or None,
                "region_name": settings.s3_region,
                "config": Config(signature_version="s3v4"),
            }
            if settings.s3_endpoint:
                kwargs["endpoint_url"] = settings.s3_endpoint
            self._client = boto3.client(**kwargs)
        return self._client

    @property
    def is_configured(self) -> bool:
        return bool(settings.s3_access_key and settings.s3_secret_key)

    def ensure_bucket(self) -> None:
        bucket = settings.s3_bucket
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            create_kwargs: dict = {"Bucket": bucket}
            if settings.s3_region != "us-east-1":
                create_kwargs["CreateBucketConfiguration"] = {
                    "LocationConstraint": settings.s3_region
                }
            self.client.create_bucket(**create_kwargs)

    def build_listing_image_key(self, listing_id: uuid.UUID, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
        return f"listings/{listing_id}/{uuid.uuid4()}.{ext}"

    def build_brand_logo_key(self, filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
        return f"brand/logo.{ext}"

    def build_public_url(self, storage_key: str) -> str:
        if settings.s3_public_url:
            return f"{settings.s3_public_url.rstrip('/')}/{storage_key}"
        if settings.s3_endpoint:
            return f"{settings.s3_endpoint.rstrip('/')}/{settings.s3_bucket}/{storage_key}"
        return f"https://{settings.s3_bucket}.s3.{settings.s3_region}.amazonaws.com/{storage_key}"

    def generate_presigned_put_url(self, storage_key: str, content_type: str) -> str:
        if not self.is_configured:
            return f"http://localhost/mock-upload/{storage_key}?content_type={content_type}"
        return self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": storage_key,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )

    def object_exists(self, storage_key: str) -> bool:
        if not self.is_configured:
            return True
        try:
            self.client.head_object(Bucket=settings.s3_bucket, Key=storage_key)
            return True
        except ClientError:
            return False

    def delete_object(self, storage_key: str) -> None:
        if not self.is_configured:
            return
        try:
            self.client.delete_object(Bucket=settings.s3_bucket, Key=storage_key)
        except ClientError as exc:
            raise StorageError("Failed to delete object.", "STORAGE_ERROR") from exc


@lru_cache
def get_storage_service() -> StorageService:
    return StorageService()
