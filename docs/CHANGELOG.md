# Changelog

All notable changes to this project are documented here.

## [0.1.0] — 2026-07-02

### Added

- **Monorepo scaffold** — `api/`, `web/`, `android/`, `ios/`, `docs/`
  - Reason: Phase 0 kickoff per product brief
- **FastAPI backend** — auth (OTP + JWT), users, dealer stores, listings, search
  - Files: `api/app/**`, `api/alembic/**`, `api/tests/**`
- **PostgreSQL schema v1** — users, dealer_stores, listings, listing_images, reviews, inquiries, favorites, reports, audit_logs
  - Migration: `api/alembic/versions/001_initial_schema.py`
- **Next.js web app** — home, search, listing detail pages with SEO metadata
  - Files: `web/src/**`
- **Android scaffold** — Kotlin + Jetpack Compose empty app
  - Files: `android/**`
- **iOS scaffold** — Swift + SwiftUI empty app
  - Files: `ios/**`
- **Docker Compose** — PostgreSQL 16, Redis 7, MinIO (dev object storage)
- **CI** — GitHub Actions: API pytest, web lint + build
- **Documentation** — full `docs/` suite per engineering standards

### Breaking changes

None — initial release.

### Migration notes

Run `alembic upgrade head` after first `docker compose up -d`.
