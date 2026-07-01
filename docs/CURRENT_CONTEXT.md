# Current Context

**Last updated:** 2026-07-02

## Current objective

Complete Phase 0 foundation: monorepo scaffold, API with auth + listings, web browse pages, mobile scaffolds, CI, and full documentation.

## Current branch

`main` (initial scaffold — not yet pushed)

## Files modified (this session)

- Entire greenfield scaffold: `api/`, `web/`, `android/`, `ios/`, `docs/`, `docker-compose.yml`, `.github/workflows/`

## Architecture summary

```
Clients (Web, Android, iOS)
        │
        ▼
   FastAPI /api/v1  ──► PostgreSQL (primary data)
        │              Redis (cache, rate limits, sessions)
        ▼
   S3/R2 (images)     Workers (future: push, search sync)
```

**Pattern:** Clean Architecture in API — `domain` → `application` → `infrastructure` → `api` (HTTP).

**Auth:** Phone OTP → JWT access token (15 min) + refresh token (30 days, rotated).

**Roles:** `guest`, `user`, `dealer`, `moderator`, `admin` — stored on User, enforced via dependency injection.

## Implementation status

| Module | Status |
|--------|--------|
| Auth (OTP + JWT) | ✅ API done, dev mock OTP |
| Users / profiles | ✅ Schema + basic endpoints |
| Dealer stores | ✅ Schema, CRUD partial |
| Listings | ✅ CRUD + search, no images yet |
| Images | ⏳ Schema ready, upload pending |
| Reviews | ⏳ Schema only |
| Messaging | ❌ Not started |
| Moderation | ⏳ Status enums, queue API pending |
| Web UI | ✅ Home, search, listing detail scaffold |
| Android | ✅ Project scaffold |
| iOS | ✅ Project scaffold |

## Open tasks

See [TASKS.md](TASKS.md).

## Known risks

- Owner decisions on moderation, privacy, monetization not finalized — defaults documented in DECISIONS.md
- No production credentials yet (SMS, storage, maps)
- Mobile apps are scaffolds only — no API integration yet

## Next recommended actions

1. Wire presigned image upload to listing create flow
2. Build inquiry endpoint + seller inbox
3. Add moderation approve/reject endpoints
4. Connect Android/iOS to auth + listing list APIs
5. Obtain owner sign-off on pending business decisions
