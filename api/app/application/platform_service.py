from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ModerationMode
from app.infrastructure.database import PlatformSettingsModel
from app.infrastructure.storage import StorageService, get_storage_service


class PlatformService:
    ROW_ID = 1

    def __init__(self, db: AsyncSession, storage: StorageService | None = None):
        self.db = db
        self.storage = storage or get_storage_service()

    async def get_or_create(self) -> PlatformSettingsModel:
        settings = await self.db.get(PlatformSettingsModel, self.ROW_ID)
        if not settings:
            settings = PlatformSettingsModel(
                id=self.ROW_ID,
                brand_name="Car-Market",
                brand_domain="carmarket.in",
                moderation_mode=ModerationMode.MANUAL,
            )
            self.db.add(settings)
            await self.db.flush()
        return settings

    async def update(
        self,
        *,
        brand_name: str | None = None,
        brand_domain: str | None = None,
        logo_url: str | None = None,
        moderation_mode: ModerationMode | None = None,
        enable_featured_listings: bool | None = None,
        enable_dealer_subscriptions: bool | None = None,
        enable_paid_listings: bool | None = None,
    ) -> PlatformSettingsModel:
        settings = await self.get_or_create()
        if brand_name is not None:
            settings.brand_name = brand_name.strip()
        if brand_domain is not None:
            settings.brand_domain = brand_domain.strip().lower()
        if logo_url is not None:
            settings.logo_url = logo_url or None
        if moderation_mode is not None:
            settings.moderation_mode = moderation_mode
        if enable_featured_listings is not None:
            settings.enable_featured_listings = enable_featured_listings
        if enable_dealer_subscriptions is not None:
            settings.enable_dealer_subscriptions = enable_dealer_subscriptions
        if enable_paid_listings is not None:
            settings.enable_paid_listings = enable_paid_listings
        await self.db.flush()
        return settings

    def presign_logo(self, *, filename: str, content_type: str) -> dict:
        storage_key = self.storage.build_brand_logo_key(filename)
        upload_url = self.storage.generate_presigned_put_url(storage_key, content_type)
        return {
            "upload_url": upload_url,
            "storage_key": storage_key,
            "content_type": content_type,
            "expires_in": 3600,
        }

    async def confirm_logo(self, storage_key: str) -> PlatformSettingsModel:
        if not storage_key.startswith("brand/"):
            raise ValueError("Invalid logo storage key")
        if not self.storage.object_exists(storage_key):
            raise ValueError("Uploaded logo not found")
        logo_url = self.storage.build_public_url(storage_key)
        return await self.update(logo_url=logo_url)
