# Database Schema

PostgreSQL 16. Migrations managed by Alembic in `api/alembic/`.

## ER diagram (core entities)

```mermaid
erDiagram
  users ||--o| dealer_stores : owns
  users ||--o{ listings : creates
  dealer_stores ||--o{ listings : publishes
  listings ||--|{ listing_images : has
  users ||--o{ reviews : writes
  users ||--o{ inquiries : sends
  listings ||--o{ inquiries : receives
  users ||--o{ favorites : saves
  users ||--o{ reports : files
  users ||--o{ audit_logs : triggers

  users {
    uuid id PK
    varchar phone UK
    varchar email
    varchar display_name
    enum role
    boolean phone_verified
    boolean email_verified
    varchar city
    timestamptz created_at
    timestamptz updated_at
    timestamptz deleted_at
  }

  dealer_stores {
    uuid id PK
    uuid owner_id FK
    varchar name
    varchar slug UK
    text description
    varchar logo_url
    varchar banner_url
    varchar address
    varchar city
    varchar state
    varchar pincode
    decimal latitude
    decimal longitude
    varchar phone
    varchar whatsapp
    jsonb business_hours
    decimal rating_avg
    int rating_count
    enum verification_status
    timestamptz created_at
  }

  listings {
    uuid id PK
    uuid seller_id FK
    uuid dealer_store_id FK
    varchar make
    varchar model
    varchar variant
    int manufacturing_year
    int registration_year
    enum body_type
    enum fuel_type
    enum transmission
    int odometer_km
    int num_owners
    varchar registration_state
    varchar registration_city
    varchar registration_number_masked
    enum rc_status
    date insurance_expiry
    date puc_expiry
    enum loan_status
    bigint asking_price
    boolean negotiable
    varchar city
    varchar locality
    varchar pincode
    enum status
    tsvector search_vector
    timestamptz published_at
    timestamptz expires_at
    timestamptz created_at
  }

  listing_images {
    uuid id PK
    uuid listing_id FK
    varchar storage_key
    varchar url
    varchar thumbnail_url
    int sort_order
    boolean is_cover
    timestamptz created_at
  }

  reviews {
    uuid id PK
    uuid reviewer_id FK
    enum target_type
    uuid target_id
    int rating
    varchar seller_reply
    enum status
    timestamptz created_at
  }

  inquiries {
    uuid id PK
    uuid listing_id FK
    uuid buyer_id FK
    uuid seller_id FK
    text message
    enum status
    timestamptz created_at
  }
```

## Indexes

| Table | Index | Purpose |
|-------|-------|---------|
| `listings` | `(status, city)` | Active listings by city |
| `listings` | `(asking_price)` | Price sort/filter |
| `listings` | `(manufacturing_year)` | Year filter |
| `listings` | `(odometer_km)` | KM filter/sort |
| `listings` | `GIN(search_vector)` | Full-text search |
| `users` | `(phone)` UNIQUE | Login lookup |
| `dealer_stores` | `(slug)` UNIQUE | Public URL |
| `listing_images` | `(listing_id, sort_order)` | Gallery order |

## Enums

- `user_role`: guest, user, dealer, moderator, admin
- `listing_status`: draft, pending_review, live, sold, expired, removed
- `fuel_type`: petrol, diesel, cng, ev, hybrid
- `transmission`: manual, automatic, amt, dct
- `body_type`: hatchback, sedan, suv, muv, coupe, convertible, pickup, van
- `rc_status`: valid, pending_transfer
- `loan_status`: cleared, ongoing
- `verification_status`: pending, verified, rejected

## Constraints

- Listing requires minimum fields before `publish` (enforced in application layer)
- Soft delete on `users` via `deleted_at`
- Registration number stored encrypted/masked; never full number in public API

## Backup policy (production)

- Daily automated PostgreSQL backup
- 30-day retention
- Point-in-time recovery enabled on managed provider
