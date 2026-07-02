"""Load six sample used-car listings (same data as local dev seed)."""

from __future__ import annotations

import json
import mimetypes
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.listing_service import ListingService
from app.core.config import settings
from app.domain.enums import ListingStatus, UserRole
from app.infrastructure.database import (
    FavoriteModel,
    InquiryModel,
    ListingImageModel,
    ListingModel,
    RecentlyViewedModel,
    UserModel,
)
from app.infrastructure.storage import StorageService, get_storage_service

SEED_ASSETS = Path(__file__).resolve().parents[2] / "seed_assets"
SEED_PHONE = "+919998887776"


@dataclass(frozen=True)
class SampleListing:
    make: str
    model: str
    variant: str
    manufacturing_year: int
    body_type: str
    fuel_type: str
    transmission: str
    odometer_km: int
    asking_price: int
    city: str
    locality: str
    image_file: str


SAMPLES: tuple[SampleListing, ...] = (
    SampleListing("Maruti", "Swift", "VXI", 2020, "hatchback", "petrol", "manual", 32000, 575000, "Pune", "Kothrud", "maruti-swift.jpeg"),
    SampleListing("Maruti", "Swift", "ZXI", 2019, "hatchback", "petrol", "manual", 41000, 520000, "Delhi", "Dwarka", "maruti-swift2.jpg"),
    SampleListing("Hyundai", "Creta", "SX", 2021, "suv", "diesel", "automatic", 45000, 1420000, "Mumbai", "Andheri", "hyundai-creta.jpg"),
    SampleListing("Hyundai", "Creta", "SX(O)", 2020, "suv", "petrol", "automatic", 52000, 1280000, "Chennai", "OMR", "hyundai-creta2.jpg"),
    SampleListing("Tata", "Nexon", "XZ+", 2022, "suv", "ev", "automatic", 18000, 1180000, "Bangalore", "Whitefield", "tata-nexon.jpg"),
    SampleListing("Tata", "Nexon", "EV Max", 2023, "suv", "ev", "automatic", 12000, 1350000, "Hyderabad", "Gachibowli", "tata-nexon2.jpg"),
)


class SampleDataService:
    def __init__(self, db: AsyncSession, storage: StorageService | None = None):
        self.db = db
        self.storage = storage or get_storage_service()
        self.listing_service = ListingService(db)

    async def seed(self) -> dict:
        self._ensure_bucket_public_read()
        seller = await self._get_or_create_seller()
        cleared = await self._clear_seller_listings(seller.id)
        created: list[str] = []

        for sample in SAMPLES:
            listing = await self.listing_service.create(
                seller,
                {
                    "make": sample.make,
                    "model": sample.model,
                    "variant": sample.variant,
                    "manufacturing_year": sample.manufacturing_year,
                    "body_type": sample.body_type,
                    "fuel_type": sample.fuel_type,
                    "transmission": sample.transmission,
                    "odometer_km": sample.odometer_km,
                    "asking_price": sample.asking_price,
                    "city": sample.city,
                    "locality": sample.locality,
                },
            )
            await self._attach_image(listing.id, sample.image_file)
            listing.status = ListingStatus.LIVE
            listing.published_at = datetime.now(UTC)
            listing.expires_at = datetime.now(UTC) + timedelta(days=settings.listing_expiry_days)
            created.append(str(listing.id))

        await self.db.commit()
        live_count = len(
            (await self.db.scalars(select(ListingModel.id).where(ListingModel.status == ListingStatus.LIVE))).all()
        )
        return {
            "cleared": cleared,
            "created": len(created),
            "listing_ids": created,
            "live_total": live_count,
        }

    async def _get_or_create_seller(self) -> UserModel:
        user = await self.db.scalar(select(UserModel).where(UserModel.phone == SEED_PHONE))
        if user:
            return user
        user = UserModel(phone=SEED_PHONE, role=UserRole.USER)
        self.db.add(user)
        await self.db.flush()
        return user

    async def _clear_seller_listings(self, seller_id: uuid.UUID) -> int:
        listing_ids = (
            await self.db.scalars(select(ListingModel.id).where(ListingModel.seller_id == seller_id))
        ).all()
        if not listing_ids:
            return 0
        await self.db.execute(delete(InquiryModel).where(InquiryModel.listing_id.in_(listing_ids)))
        await self.db.execute(delete(FavoriteModel).where(FavoriteModel.listing_id.in_(listing_ids)))
        await self.db.execute(
            delete(RecentlyViewedModel).where(RecentlyViewedModel.listing_id.in_(listing_ids))
        )
        await self.db.execute(delete(ListingImageModel).where(ListingImageModel.listing_id.in_(listing_ids)))
        await self.db.execute(delete(ListingModel).where(ListingModel.id.in_(listing_ids)))
        await self.db.flush()
        return len(listing_ids)

    async def _attach_image(self, listing_id: uuid.UUID, filename: str) -> None:
        path = SEED_ASSETS / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing seed image: {filename}")

        content_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
        storage_key = self.storage.build_listing_image_key(listing_id, filename)
        body = path.read_bytes()

        if self.storage.is_configured:
            self.storage.client.put_object(
                Bucket=settings.s3_bucket,
                Key=storage_key,
                Body=body,
                ContentType=content_type,
            )
        else:
            storage_key = f"listings/{listing_id}/{filename}"

        image = ListingImageModel(
            listing_id=listing_id,
            storage_key=storage_key,
            url=self.storage.build_public_url(storage_key),
            sort_order=0,
            is_cover=True,
        )
        self.db.add(image)
        await self.db.flush()

    def _ensure_bucket_public_read(self) -> None:
        if not self.storage.is_configured:
            return
        bucket = settings.s3_bucket
        policy = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket}/*"],
                    }
                ],
            }
        )
        try:
            self.storage.client.put_bucket_policy(Bucket=settings.s3_bucket, Policy=policy)
        except Exception:
            pass
