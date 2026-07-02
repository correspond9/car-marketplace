"""Seed sample listings for local development."""

import asyncio
import mimetypes
import uuid
from pathlib import Path

import httpx

API = "http://localhost:8000/api/v1"
OTP = "123456"
REPO_ROOT = Path(__file__).resolve().parents[2]
MEDIA_DIR = REPO_ROOT / "Media"


async def upload_listing_image(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    listing_id: str,
    image_path: Path,
) -> None:
    if not image_path.is_file():
        print(f"  skip missing image: {image_path.name}")
        return

    content_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    presign = await client.post(
        f"/listings/{listing_id}/images/presign",
        json={"filename": image_path.name, "content_type": content_type},
        headers=headers,
    )
    presign.raise_for_status()
    payload = presign.json()
    image_bytes = image_path.read_bytes()
    upload = await client.put(
        payload["upload_url"],
        content=image_bytes,
        headers={"Content-Type": content_type},
    )
    upload.raise_for_status()
    confirm = await client.post(
        f"/listings/{listing_id}/images/confirm",
        json={
            "storage_key": payload["storage_key"],
            "sort_order": 0,
            "is_cover": True,
        },
        headers=headers,
    )
    confirm.raise_for_status()


async def clear_dev_listings() -> None:
    from sqlalchemy import delete, select
    from app.infrastructure.database import (
        FavoriteModel,
        InquiryModel,
        ListingImageModel,
        ListingModel,
        RecentlyViewedModel,
        UserModel,
        async_session_factory,
    )

    async with async_session_factory() as session:
        user = await session.scalar(select(UserModel).where(UserModel.phone == "+919998887776"))
        if not user:
            return
        listing_ids = (
            await session.scalars(select(ListingModel.id).where(ListingModel.seller_id == user.id))
        ).all()
        if not listing_ids:
            return
        await session.execute(delete(InquiryModel).where(InquiryModel.listing_id.in_(listing_ids)))
        await session.execute(delete(FavoriteModel).where(FavoriteModel.listing_id.in_(listing_ids)))
        await session.execute(
            delete(RecentlyViewedModel).where(RecentlyViewedModel.listing_id.in_(listing_ids))
        )
        await session.execute(delete(ListingImageModel).where(ListingImageModel.listing_id.in_(listing_ids)))
        await session.execute(delete(ListingModel).where(ListingModel.id.in_(listing_ids)))
        await session.commit()
        print(f"Cleared {len(listing_ids)} old dev listings.")


async def main() -> None:
    await clear_dev_listings()
    async with httpx.AsyncClient(base_url=API, timeout=30.0) as client:
        phone = "9998887776"
        await client.post("/auth/otp/request", json={"phone": phone})
        auth = await client.post("/auth/otp/verify", json={"phone": phone, "otp": OTP})
        auth.raise_for_status()
        token = auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Six listings — one royalty-free photo each, matched by car name in Media/
        samples = [
            {
                "make": "Maruti",
                "model": "Swift",
                "variant": "VXI",
                "manufacturing_year": 2020,
                "body_type": "hatchback",
                "fuel_type": "petrol",
                "transmission": "manual",
                "odometer_km": 32000,
                "asking_price": 575000,
                "city": "Pune",
                "locality": "Kothrud",
                "image": MEDIA_DIR / "maruti-swift.jpeg",
            },
            {
                "make": "Maruti",
                "model": "Swift",
                "variant": "ZXI",
                "manufacturing_year": 2019,
                "body_type": "hatchback",
                "fuel_type": "petrol",
                "transmission": "manual",
                "odometer_km": 41000,
                "asking_price": 520000,
                "city": "Delhi",
                "locality": "Dwarka",
                "image": MEDIA_DIR / "maruti-swift2.jpg",
            },
            {
                "make": "Hyundai",
                "model": "Creta",
                "variant": "SX",
                "manufacturing_year": 2021,
                "body_type": "suv",
                "fuel_type": "diesel",
                "transmission": "automatic",
                "odometer_km": 45000,
                "asking_price": 1420000,
                "city": "Mumbai",
                "locality": "Andheri",
                "image": MEDIA_DIR / "hyundai creta.jpg",
            },
            {
                "make": "Hyundai",
                "model": "Creta",
                "variant": "SX(O)",
                "manufacturing_year": 2020,
                "body_type": "suv",
                "fuel_type": "petrol",
                "transmission": "automatic",
                "odometer_km": 52000,
                "asking_price": 1280000,
                "city": "Chennai",
                "locality": "OMR",
                "image": MEDIA_DIR / "hyundai-creta2.jpg",
            },
            {
                "make": "Tata",
                "model": "Nexon",
                "variant": "XZ+",
                "manufacturing_year": 2022,
                "body_type": "suv",
                "fuel_type": "ev",
                "transmission": "automatic",
                "odometer_km": 18000,
                "asking_price": 1180000,
                "city": "Bangalore",
                "locality": "Whitefield",
                "image": MEDIA_DIR / "tata-nexon.jpg",
            },
            {
                "make": "Tata",
                "model": "Nexon",
                "variant": "EV Max",
                "manufacturing_year": 2023,
                "body_type": "suv",
                "fuel_type": "ev",
                "transmission": "automatic",
                "odometer_km": 12000,
                "asking_price": 1350000,
                "city": "Hyderabad",
                "locality": "Gachibowli",
                "image": MEDIA_DIR / "tata-nexon2.jpg",
            },
        ]

        created_ids: list[uuid.UUID] = []
        for data in samples:
            image_path = data.pop("image")
            resp = await client.post("/listings", json=data, headers=headers)
            resp.raise_for_status()
            listing_id = resp.json()["id"]
            created_ids.append(uuid.UUID(listing_id))
            await upload_listing_image(client, headers, listing_id, image_path)
            await client.post(f"/listings/{listing_id}/publish", headers=headers)

        print(f"Created and submitted {len(created_ids)} listings for moderation.")

        from sqlalchemy import update
        from app.domain.enums import ListingStatus, UserRole
        from app.infrastructure.database import ListingModel, UserModel, async_session_factory

        async with async_session_factory() as session:
            await session.execute(
                update(UserModel)
                .where(UserModel.phone == "+919998887776")
                .values(role=UserRole.MODERATOR)
            )
            await session.execute(
                update(ListingModel)
                .where(ListingModel.id.in_(created_ids))
                .values(status=ListingStatus.LIVE)
            )
            await session.commit()

        search = await client.get("/listings")
        search.raise_for_status()
        total = search.json()["total"]
        print(f"Live listings visible in search: {total}")


if __name__ == "__main__":
    asyncio.run(main())
