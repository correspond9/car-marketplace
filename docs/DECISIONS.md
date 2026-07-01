# Architectural & Product Decisions

## ADR-001: Monorepo vs multi-repo

| | |
|---|---|
| **Problem** | Brief recommends separate repos; workspace is single folder |
| **Options** | Multi-repo; monorepo with `api/`, `web/`, `android/`, `ios/` |
| **Chosen** | Monorepo |
| **Reason** | Single workspace for AI handoff, shared CI, atomic docs; can split later |
| **Advantages** | Easier onboarding, one clone, unified changelog |
| **Tradeoffs** | Larger repo; mobile teams may prefer separate remotes later |

---

## ADR-002: Backend framework

| | |
|---|---|
| **Problem** | Choose API framework |
| **Options** | FastAPI (Python), NestJS (Node) |
| **Chosen** | FastAPI 0.115+ with SQLAlchemy 2.0 |
| **Reason** | Mature typing, auto OpenAPI, strong ecosystem for file/background jobs |
| **Advantages** | Fast dev, excellent docs generation, async support |
| **Tradeoffs** | Python GIL for CPU-heavy tasks (offensive: workers) |

---

## ADR-003: Web framework

| | |
|---|---|
| **Problem** | SEO-critical listing pages |
| **Options** | Next.js, Nuxt |
| **Chosen** | Next.js 15 App Router |
| **Reason** | SSR/SSG for SEO, Schema.org, largest hiring pool |
| **Advantages** | ISR for listing pages, image optimization |
| **Tradeoffs** | Vercel-optimized; self-host requires Node |

---

## ADR-004: Search v1

| | |
|---|---|
| **Problem** | Faceted car search at launch |
| **Options** | PostgreSQL FTS + filters; Meilisearch day one |
| **Chosen** | PostgreSQL full-text + indexed filters |
| **Reason** | Simpler ops for v1; migrate to Meilisearch in Phase 2 |
| **Advantages** | No extra service; transactional consistency |
| **Tradeoffs** | Weaker relevance/faceting at very large scale |

---

## ADR-005: Auth model

| | |
|---|---|
| **Problem** | India market expects phone OTP |
| **Options** | Password; OTP-only; OAuth social |
| **Chosen** | Phone OTP primary; optional email; JWT + refresh |
| **Reason** | Standard for Indian marketplaces; no password reset burden |
| **Advantages** | Lower friction signup |
| **Tradeoffs** | SMS cost; needs provider (MSG91) in prod |

---

## ADR-006: Listing moderation default ⚠️ PENDING OWNER

| | |
|---|---|
| **Problem** | Auto-publish vs manual approval |
| **Options** | Auto-live; manual queue; auto for trusted dealers |
| **Chosen (interim)** | **Manual approval** for all new listings |
| **Reason** | Trust/safety at launch; reduces scam exposure |
| **Advantages** | Quality control |
| **Tradeoffs** | Slower time-to-live; needs moderator staffing |
| **Status** | **Awaiting owner confirmation** |

---

## ADR-007: Contact privacy ⚠️ PENDING OWNER

| | |
|---|---|
| **Problem** | When to show seller phone/email |
| **Options** | Always hidden; show for dealers; show after inquiry accepted |
| **Chosen (interim)** | **Hidden until seller accepts inquiry** |
| **Reason** | Reduces spam; aligns with brief recommendation |
| **Status** | **Awaiting owner confirmation** |

---

## ADR-008: Monetization v1 ⚠️ PENDING OWNER

| | |
|---|---|
| **Problem** | Paid features at launch |
| **Options** | Free only; featured listings; dealer subscription |
| **Chosen (interim)** | **Free connect-only** — no payments in v1 |
| **Reason** | Brief recommends PMF before monetization |
| **Status** | **Awaiting owner confirmation** |

---

## ADR-009: Brand placeholder ⚠️ PENDING OWNER

| | |
|---|---|
| **Problem** | No finalized brand/domain |
| **Chosen (interim)** | Code name **CarMarket**, domain placeholder `carmarket.in` |
| **Status** | **Awaiting owner confirmation**

---

## ADR-010: Image storage

| | |
|---|---|
| **Problem** | Multi-photo listings, CDN delivery |
| **Options** | AWS S3; Cloudflare R2; MinIO self-hosted |
| **Chosen** | S3-compatible API — **MinIO dev**, **R2/S3 prod** |
| **Reason** | Presigned direct upload; CDN-friendly |
| **Advantages** | Scalable, offloads API bandwidth |
| **Tradeoffs** | Extra service to operate |

---

## ADR-011: Mobile architecture

| | |
|---|---|
| **Problem** | Brief forbids WebView shells |
| **Chosen** | Kotlin + Jetpack Compose (Android); Swift + SwiftUI (iOS) |
| **Code sharing** | OpenAPI-generated clients only; design tokens JSON optional |
| **Reason** | Native UX, store compliance, camera/gallery integration |
