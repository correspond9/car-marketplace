import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_otp_verify(client: AsyncClient) -> None:
    phone = "9123456789"
    req = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert req.status_code == 204
    verify = await client.post(
        "/api/v1/auth/otp/verify", json={"phone": phone, "otp": "123456"}
    )
    assert verify.status_code == 200
    data = verify.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_create_and_search_listing(client: AsyncClient, auth_headers: dict) -> None:
    create = await client.post(
        "/api/v1/listings",
        json={
            "make": "Maruti",
            "model": "Swift",
            "manufacturing_year": 2020,
            "body_type": "hatchback",
            "fuel_type": "petrol",
            "transmission": "manual",
            "odometer_km": 35000,
            "asking_price": 550000,
            "city": "Pune",
        },
        headers=auth_headers,
    )
    assert create.status_code == 201
    listing_id = create.json()["id"]

    for i in range(5):
        presign = await client.post(
            f"/api/v1/listings/{listing_id}/images/presign",
            json={"filename": f"car{i}.jpg", "content_type": "image/jpeg"},
            headers=auth_headers,
        )
        assert presign.status_code == 200
        storage_key = presign.json()["storage_key"]
        confirm = await client.post(
            f"/api/v1/listings/{listing_id}/images/confirm",
            json={"storage_key": storage_key, "sort_order": i},
            headers=auth_headers,
        )
        assert confirm.status_code == 201

    publish = await client.post(f"/api/v1/listings/{listing_id}/publish", headers=auth_headers)
    assert publish.status_code == 200
    assert publish.json()["status"] == "pending_review"

    search = await client.get("/api/v1/listings", params={"q": "Swift"})
    assert search.status_code == 200
    assert search.json()["total"] == 0

    me = await client.get("/api/v1/users/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["phone_verified"] is True
