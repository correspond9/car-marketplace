import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


LISTING_PAYLOAD = {
    "make": "Maruti",
    "model": "Swift",
    "manufacturing_year": 2020,
    "body_type": "hatchback",
    "fuel_type": "petrol",
    "transmission": "manual",
    "odometer_km": 35000,
    "asking_price": 550000,
    "city": "Pune",
}


async def _auth(client: AsyncClient, phone: str) -> dict[str, str]:
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    response = await client.post(
        "/api/v1/auth/otp/verify", json={"phone": phone, "otp": "123456"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_live_listing(
    client: AsyncClient, headers: dict, moderator_headers: dict | None = None
) -> str:
    create = await client.post("/api/v1/listings", json=LISTING_PAYLOAD, headers=headers)
    listing_id = create.json()["id"]
    for i in range(5):
        presign = await client.post(
            f"/api/v1/listings/{listing_id}/images/presign",
            json={"filename": f"photo{i}.jpg", "content_type": "image/jpeg"},
            headers=headers,
        )
        storage_key = presign.json()["storage_key"]
        await client.post(
            f"/api/v1/listings/{listing_id}/images/confirm",
            json={"storage_key": storage_key, "sort_order": i, "is_cover": i == 0},
            headers=headers,
        )
    await client.post(f"/api/v1/listings/{listing_id}/publish", headers=headers)
    if moderator_headers:
        await client.post(
            f"/api/v1/moderation/listings/{listing_id}/approve",
            headers=moderator_headers,
        )
    return listing_id


@pytest.mark.asyncio
async def test_dealer_listing_shows_contact_by_default(
    client: AsyncClient, moderator_headers: dict[str, str]
) -> None:
    dealer_headers = await _auth(client, "9555555555")
    await client.post(
        "/api/v1/dealer-stores",
        json={"name": "Contact Motors", "city": "Mumbai", "phone": "9555555555"},
        headers=dealer_headers,
    )
    create = await client.post("/api/v1/listings", json=LISTING_PAYLOAD, headers=dealer_headers)
    assert create.json()["show_contact_publicly"] is True

    listing_id = await _create_live_listing(client, dealer_headers, moderator_headers)
    listing = await client.get(f"/api/v1/listings/{listing_id}", headers=dealer_headers)
    assert listing.json()["seller_contact_phone"] is not None


@pytest.mark.asyncio
async def test_auto_moderation_publishes_live(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    from app.application.platform_service import PlatformService
    from app.domain.enums import ModerationMode

    await PlatformService(db_session).update(moderation_mode=ModerationMode.AUTO)

    seller_headers = await _auth(client, "9666666666")
    create = await client.post("/api/v1/listings", json=LISTING_PAYLOAD, headers=seller_headers)
    listing_id = create.json()["id"]
    for i in range(5):
        presign = await client.post(
            f"/api/v1/listings/{listing_id}/images/presign",
            json={"filename": f"photo{i}.jpg", "content_type": "image/jpeg"},
            headers=seller_headers,
        )
        storage_key = presign.json()["storage_key"]
        await client.post(
            f"/api/v1/listings/{listing_id}/images/confirm",
            json={"storage_key": storage_key, "sort_order": i, "is_cover": i == 0},
            headers=seller_headers,
        )
    publish = await client.post(f"/api/v1/listings/{listing_id}/publish", headers=seller_headers)
    assert publish.json()["status"] == "live"


@pytest.mark.asyncio
async def test_platform_settings_public(client: AsyncClient) -> None:
    response = await client.get("/api/v1/platform/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["brand_name"] == "Car-Market"
    assert data["brand_domain"] == "carmarket.in"


@pytest.mark.asyncio
async def test_dealer_store_create_and_public(client: AsyncClient) -> None:
    headers = await _auth(client, "9111111111")
    response = await client.post(
        "/api/v1/dealer-stores",
        json={"name": "Pune Motors", "city": "Pune", "phone": "9111111111"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "pune-motors"
    assert data["verification_status"] == "pending"

    public = await client.get(f"/api/v1/dealer-stores/{data['slug']}", headers=headers)
    assert public.status_code == 200
    assert public.json()["name"] == "Pune Motors"

    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.json()["role"] == "dealer"


@pytest.mark.asyncio
async def test_favorite_add_list_remove(client: AsyncClient, auth_headers: dict) -> None:
    seller_headers = auth_headers
    listing_id = await _create_live_listing(client, seller_headers)

    buyer_headers = await _auth(client, "9222222222")
    add = await client.post(f"/api/v1/favorites/{listing_id}", headers=buyer_headers)
    assert add.status_code == 201

    listing = await client.get(f"/api/v1/listings/{listing_id}", headers=buyer_headers)
    assert listing.status_code == 200

    favs = await client.get("/api/v1/favorites", headers=buyer_headers)
    assert favs.status_code == 200
    assert favs.json()["total"] == 1
    assert favs.json()["items"][0]["id"] == listing_id

    remove = await client.delete(f"/api/v1/favorites/{listing_id}", headers=buyer_headers)
    assert remove.status_code == 204

    favs_after = await client.get("/api/v1/favorites", headers=buyer_headers)
    assert favs_after.json()["total"] == 0


@pytest.mark.asyncio
async def test_inquiry_phone_hidden_until_accepted(
    client: AsyncClient, moderator_headers: dict[str, str]
) -> None:
    seller_headers = await _auth(client, "9333333333")
    listing_id = await _create_live_listing(client, seller_headers, moderator_headers)

    buyer_headers = await _auth(client, "9444444444")
    create = await client.post(
        f"/api/v1/listings/{listing_id}/inquiries",
        json={"message": "Is this car still available?"},
        headers=buyer_headers,
    )
    assert create.status_code == 201
    inquiry = create.json()
    assert inquiry["seller_phone"] is None

    sent = await client.get("/api/v1/inquiries/sent", headers=buyer_headers)
    assert sent.json()["items"][0]["seller_phone"] is None

    inbox = await client.get("/api/v1/inquiries/inbox", headers=seller_headers)
    assert inbox.json()["items"][0]["buyer_phone"] == "+919444444444"

    accept = await client.patch(
        f"/api/v1/inquiries/{inquiry['id']}/accept",
        headers=seller_headers,
    )
    assert accept.status_code == 200

    sent_after = await client.get("/api/v1/inquiries/sent", headers=buyer_headers)
    assert sent_after.json()["items"][0]["seller_phone"] == "+919333333333"
