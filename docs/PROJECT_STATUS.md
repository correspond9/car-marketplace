# Project Status

**Last updated:** 2026-07-02T00:00:00Z

## Overview

| Metric | Value |
|--------|-------|
| **Completed** | ~15% |
| **Current milestone** | Phase 0 — Foundation |
| **Current sprint** | Sprint 1 — Repo scaffold + Auth + Listing core |
| **Target** | Production MVP (Phase 1) |

## Completed modules

- [x] Monorepo structure (`api`, `web`, `android`, `ios`)
- [x] Documentation suite (`docs/`)
- [x] Architectural decisions recorded (with owner-pending items flagged)
- [x] Docker Compose (PostgreSQL 16, Redis 7)
- [x] FastAPI backend scaffold with clean architecture layers
- [x] Database schema v1 + Alembic migrations
- [x] Auth: OTP request/verify, JWT access + refresh tokens, role-based access
- [x] User & dealer store domain models
- [x] Listing CRUD (draft → pending → live lifecycle)
- [x] Public search with filters (PostgreSQL full-text v1)
- [x] Next.js web scaffold with listing browse/detail pages
- [x] Android & iOS project scaffolds
- [x] GitHub Actions CI (API tests, web lint/build)
- [x] OpenAPI spec at `api/openapi.yaml`

## In progress

- [ ] Image upload pipeline (presigned URLs + S3/R2)
- [ ] Messaging / inquiries
- [ ] Reviews system
- [ ] Moderation admin UI
- [ ] Push notifications (FCM)

## Blocked — owner decisions required

| Item | Default assumed | Status |
|------|-----------------|--------|
| Listing moderation | Manual approval for new listings | **Pending owner confirm** |
| Phone/email visibility | Hidden until seller accepts inquiry | **Pending owner confirm** |
| Monetization v1 | Free connect-only | **Pending owner confirm** |
| Brand name & domain | Placeholder: CarMarket / carmarket.in | **Pending owner confirm** |
| SMS OTP provider credentials | Dev mock OTP (`123456`) | **Needs MSG91/Twilio keys** |
| Object storage credentials | Local MinIO in dev | **Needs R2/S3 prod keys** |

## Next priorities

1. Image upload pipeline with presigned URLs
2. Dealer store public pages
3. Inquiry/messaging MVP
4. Moderation queue API + admin web views
5. Native mobile: auth + browse + listing detail

## Estimated remaining work

| Phase | Duration estimate |
|-------|-------------------|
| Phase 0 completion | 2–3 weeks |
| Phase 1 MVP | 6–8 weeks |
| Phase 2 Growth | Ongoing |
