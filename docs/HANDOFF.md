# Handoff Document

**Milestone:** Phase 0 Foundation — Initial Scaffold  
**Date:** 2026-07-02  
**Branch:** `main`

## Current status

Greenfield monorepo created with production-oriented API, web scaffold, mobile scaffolds, Docker dev environment, CI, and full documentation. Auth + listing core API is functional in development. ~15% of total MVP complete.

## Completed work

1. Documentation suite in `/docs`
2. FastAPI backend with Clean Architecture
3. PostgreSQL schema + Alembic migration `001_initial_schema`
4. OTP auth (dev mock) + JWT access/refresh
5. Listing CRUD + public search
6. Next.js web: home, search, listing detail
7. Android (Compose) + iOS (SwiftUI) empty apps
8. Docker Compose: Postgres, Redis, MinIO
9. GitHub Actions CI

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md). Summary: REST API `/api/v1`, JWT auth, PostgreSQL primary store, Redis cache/rate limits, S3-compatible image storage.

## Folder structure

```
Cars-Marketplace-Apps/
├── api/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # HTTP routes
│   │   ├── application/ # Business services
│   │   ├── core/        # Config, security, deps
│   │   ├── domain/      # Entities, enums
│   │   └── infrastructure/
│   ├── alembic/
│   ├── tests/
│   └── openapi.yaml
├── web/                 # Next.js 15
├── android/             # Kotlin Compose
├── ios/                 # SwiftUI
├── docs/                # All project docs
├── docker-compose.yml
└── .github/workflows/
```

## Pending work

1. Image upload pipeline (presigned URLs)
2. Messaging/inquiries
3. Reviews
4. Moderation queue + admin UI
5. Mobile API integration
6. Legal pages
7. Production credentials (SMS, storage)

## Pending owner decisions

Documented in [DECISIONS.md](DECISIONS.md) ADR-006 through ADR-009:
- Moderation default (interim: manual approval)
- Contact privacy (interim: hide until inquiry accepted)
- Monetization v1 (interim: free)
- Brand/domain name

## How to resume

1. Read [CURRENT_CONTEXT.md](CURRENT_CONTEXT.md)
2. Read [TASKS.md](TASKS.md) — pick top TODO item
3. Start infra: `docker compose up -d`
4. API: `cd api && alembic upgrade head && uvicorn app.main:app --reload`
5. Web: `cd web && npm run dev`

## Important files

| File | Purpose |
|------|---------|
| `api/app/main.py` | FastAPI entry |
| `api/app/core/config.py` | Settings |
| `api/app/application/auth_service.py` | OTP + JWT logic |
| `api/app/application/listing_service.py` | Listing business rules |
| `api/alembic/versions/001_initial_schema.py` | DB schema |
| `web/src/lib/api.ts` | Web API client |
| `docker-compose.yml` | Local services |

## Known issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md).

## Recent changes

See [CHANGELOG.md](CHANGELOG.md) — v0.1.0 initial scaffold.

## Recommended next task

**Implement presigned image upload flow** — unblocks listing photos, required before MVP demo.

## Assumptions made

- Monorepo acceptable (brief suggested multi-repo)
- Brand placeholder "CarMarket" until owner decides
- Manual listing moderation at launch
- Dev OTP is always `123456`
- English-only UI for v1
- Free platform, no payments in v1
