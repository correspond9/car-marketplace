# API Reference

Base URL: `https://api.carmarket.in/api/v1` (production placeholder)

Interactive docs: `/docs` (Swagger UI), `/redoc` (ReDoc)

Full OpenAPI spec: [`api/openapi.yaml`](../api/openapi.yaml)

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/otp/request` | Request OTP for phone number |
| POST | `/auth/otp/verify` | Verify OTP, receive tokens |
| POST | `/auth/refresh` | Rotate refresh token |
| POST | `/auth/logout` | Invalidate refresh token |
| DELETE | `/auth/account` | Delete account (authenticated) |

## Users

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/users/me` | User+ | Current profile |
| PATCH | `/users/me` | User+ | Update profile |
| GET | `/users/{id}` | Public | Public profile (limited fields) |

## Dealer stores

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/dealer-stores` | Dealer+ | Create store |
| GET | `/dealer-stores/{slug}` | Public | Public store page |
| PATCH | `/dealer-stores/me` | Dealer+ | Update own store |
| GET | `/dealer-stores/me/listings` | Dealer+ | Store inventory |

## Listings

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/listings` | Public | Search & filter |
| GET | `/listings/{id}` | Public | Listing detail |
| POST | `/listings` | User+ | Create listing (draft) |
| PATCH | `/listings/{id}` | Owner | Update listing |
| POST | `/listings/{id}/publish` | Owner | Submit for review / go live |
| DELETE | `/listings/{id}` | Owner/Mod | Remove listing |
| POST | `/listings/{id}/images/presign` | Owner | Get presigned upload URL |

### Search query parameters

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Full-text search |
| `make` | string | Vehicle make |
| `model` | string | Vehicle model |
| `min_price`, `max_price` | int | Price range (₹) |
| `min_year`, `max_year` | int | Manufacturing year |
| `max_km` | int | Maximum odometer |
| `fuel` | enum | petrol, diesel, cng, ev, hybrid |
| `transmission` | enum | manual, automatic, amt, dct |
| `body_type` | enum | hatchback, sedan, suv, … |
| `city` | string | City name |
| `state` | string | State code |
| `seller_type` | enum | individual, dealer |
| `sort` | enum | relevance, price_asc, price_desc, newest, lowest_km |
| `page`, `limit` | int | Pagination |

## Moderation (Moderator+)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/moderation/listings` | Pending queue |
| POST | `/moderation/listings/{id}/approve` | Approve listing |
| POST | `/moderation/listings/{id}/reject` | Reject with reason |

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| GET | `/health/ready` | Readiness (DB + Redis) |

## Error format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": []
  }
}
```

## Rate limits

| Endpoint | Limit |
|----------|-------|
| OTP request | 3 per phone per 15 min |
| Search | 60 req/min per IP |
| Authenticated API | 120 req/min per user |
