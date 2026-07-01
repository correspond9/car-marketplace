import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import ListingImageModel, ListingModel, UserModel
from app.infrastructure.storage import StorageError, StorageService, get_storage_service


class ImageError(Exception):
    def __init__(self, message: str, code: str = "IMAGE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ImageService:
    MAX_IMAGES_PER_LISTING = 20

    def __init__(self, db: AsyncSession, storage: StorageService | None = None):
        self.db = db
        self.storage = storage or get_storage_service()

    def _assert_owner(self, listing: ListingModel, user: UserModel) -> None:
        if listing.seller_id != user.id:
            raise ImageError("Not authorized.", "FORBIDDEN")

    async def presign(
        self,
        listing: ListingModel,
        user: UserModel,
        *,
        filename: str,
        content_type: str,
    ) -> dict:
        self._assert_owner(listing, user)
        count = await self.db.scalar(
            select(func.count()).select_from(ListingImageModel).where(
                ListingImageModel.listing_id == listing.id
            )
        )
        if count and count >= self.MAX_IMAGES_PER_LISTING:
            raise ImageError("Maximum images reached for this listing.", "LIMIT_REACHED")

        storage_key = self.storage.build_listing_image_key(listing.id, filename)
        upload_url = self.storage.generate_presigned_put_url(storage_key, content_type)
        return {
            "upload_url": upload_url,
            "storage_key": storage_key,
            "content_type": content_type,
            "expires_in": 3600,
        }

    async def confirm(
        self,
        listing: ListingModel,
        user: UserModel,
        *,
        storage_key: str,
        sort_order: int = 0,
        is_cover: bool = False,
    ) -> ListingImageModel:
        self._assert_owner(listing, user)
        if not storage_key.startswith(f"listings/{listing.id}/"):
            raise ImageError("Invalid storage key for this listing.", "VALIDATION_ERROR")
        if not self.storage.object_exists(storage_key):
            raise ImageError("Uploaded object not found.", "NOT_FOUND")

        if is_cover:
            for image in listing.images or []:
                image.is_cover = False

        image = ListingImageModel(
            listing_id=listing.id,
            storage_key=storage_key,
            url=self.storage.build_public_url(storage_key),
            sort_order=sort_order,
            is_cover=is_cover or not (listing.images and len(listing.images) > 0),
        )
        self.db.add(image)
        await self.db.flush()
        return image

    async def delete_image(
        self, listing: ListingModel, user: UserModel, image_id: uuid.UUID
    ) -> None:
        self._assert_owner(listing, user)
        result = await self.db.execute(
            select(ListingImageModel).where(
                ListingImageModel.id == image_id,
                ListingImageModel.listing_id == listing.id,
            )
        )
        image = result.scalar_one_or_none()
        if not image:
            raise ImageError("Image not found.", "NOT_FOUND")
        try:
            self.storage.delete_object(image.storage_key)
        except StorageError:
            pass
        await self.db.delete(image)
        await self.db.flush()
