"""Seed sample listings for local development."""

import asyncio
import uuid

import httpx

API = "http://localhost:8000/api/v1"
OTP = "123456"


async def main() -> None:
    async with httpx.AsyncClient(base_url=API, timeout=30.0) as client:
        phone = "9998887776"
        await client.post("/auth/otp/request", json={"phone": phone})
        auth = await client.post("/auth/otp/verify", json={"phone": phone, "otp": OTP})
        auth.raise_for_status()
        token = auth.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

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
            },
        ]

        created_ids: list[uuid.UUID] = []
        for data in samples:
            resp = await client.post("/listings", json=data, headers=headers)
            resp.raise_for_status()
            listing_id = resp.json()["id"]
            created_ids.append(uuid.UUID(listing_id))
            await client.post(f"/listings/{listing_id}/publish", headers=headers)

        print(f"Created and submitted {len(created_ids)} listings for moderation.")

        # Promote user to moderator and approve listings
        from sqlalchemy import select, update
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
