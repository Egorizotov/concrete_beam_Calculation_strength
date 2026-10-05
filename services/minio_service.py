import io
from datetime import timedelta

from minio import Minio

from core.config import settings


class MinioService:
    def __init__(self) -> None:
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload(self, file_bytes: bytes, filename: str, content_type: str) -> str:
        """Загружает файл и возвращает публичный URL."""
        self.client.put_object(
            self.bucket,
            filename,
            io.BytesIO(file_bytes),
            length=len(file_bytes),
            content_type=content_type,
        )
        return f"{settings.MINIO_PUBLIC_URL}/{filename}"

    def remove(self, filename: str) -> None:
        try:
            self.client.remove_object(self.bucket, filename)
        except Exception as e:
            print(f"MinIO remove error: {e}")


minio_service = MinioService()