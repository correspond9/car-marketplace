# Project Status

**Last updated:** 2026-07-02

## Overview

| Metric | Value |
|--------|-------|
| **Completed** | ~85% of Phase 0 + Phase 1 MVP |
| **Current milestone** | Phase 1 MVP — feature complete (dev) |
| **Target** | Production deployment + store release |

## Completed (matches product brief)

### Backend API
- Auth: OTP, JWT, refresh, account delete, data export (DPDP)
- Listings: full CRUD, publish, sold, renew, duplicate, 5-photo rule, image presign/confirm
- Search with filters; dealer stores; inquiries (phone hidden until accepted)
- Reviews (post-inquiry); favorites; saved searches; reports
- Moderation queue; admin stats, role updates, dealer verification, audit logs
- Notifications (in-app); recently viewed tracking

### Website
- Login, sell car (with photos), my listings, favorites, compare (4 cars)
- Dealer store pages, admin moderation, legal pages (Terms/Privacy/Disclaimer)
- Help centre FAQ, SEO (sitemap, robots, city landing pages)
- Contact seller inquiry flow

### Mobile (native Kotlin + SwiftUI)
- OTP login, browse, search, detail, sell with photos, favorites, my listings
- Contact seller, profile, logout, delete account

### Infrastructure
- Docker Compose, CI, migrations, OpenAPI spec, documentation

## Still pending (brief Phase 2 / 3 or external deps)

| Item | Why not done |
|------|----------------|
| **Production SMS (MSG91)** | Needs your API keys |
| **Production storage CDN (R2/S3)** | Needs cloud credentials |
| **Push notifications (FCM/APNs)** | Needs Firebase + Apple certs |
| **Google Maps SDK in apps** | Needs Maps API key |
| **Hindi UI** | Phase 2 in brief |
| **Meilisearch** | Phase 2 in brief |
| **Razorpay / monetization** | Phase 2 + owner decision |
| **Escrow / payments** | Phase 3 + legal review |
| **Figma / PRD documents** | Design deliverables, not code |
| **Play Store / App Store submission** | Needs developer accounts + signing |
| **99.5% uptime / prod deployment** | Needs hosting choice + deploy runbook execution |

## Owner decisions still required

See `docs/DECISIONS.md` — moderation default, phone visibility, monetization, brand/domain.
