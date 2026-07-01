# Tasks (Kanban)

## TODO

- [ ] Wire presigned image upload + listing image confirm
- [ ] Inquiry/messaging endpoints + seller inbox
- [ ] Review create (verified interaction gate)
- [ ] Moderation queue approve/reject API
- [ ] Admin seed script + config endpoints
- [ ] Favorites CRUD
- [ ] Report listing endpoint
- [ ] Account deletion flow
- [ ] Legal pages (Terms, Privacy) on web
- [ ] Android: OTP login + listing feed
- [ ] iOS: OTP login + listing feed
- [ ] Push notification worker (FCM)

## IN PROGRESS

- [x] Phase 0 monorepo scaffold _(completing this sprint)_

## TESTING

- [ ] E2E: auth flow
- [ ] E2E: listing create → publish → search
- [ ] Load test search endpoint

## COMPLETED

- [x] Documentation suite
- [x] Docker Compose (Postgres, Redis, MinIO)
- [x] FastAPI backend scaffold
- [x] Database migration v1
- [x] Auth OTP + JWT
- [x] Listing CRUD + search
- [x] Next.js web scaffold
- [x] Android/iOS scaffolds
- [x] GitHub Actions CI

## BLOCKED

| Task | Blocker |
|------|---------|
| Production SMS OTP | MSG91/Twilio API keys |
| Production image CDN | R2/S3 credentials |
| Brand/deep links | Owner domain decision |
| Monetization features | Owner monetization decision |
| Legal pages final text | Legal review |
