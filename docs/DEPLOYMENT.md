# Deployment

## Environments

| Env | Purpose | URL (placeholder) |
|-----|---------|-------------------|
| Development | Local Docker | localhost |
| Staging | Pre-prod QA | staging.carmarket.in |
| Production | Live users | carmarket.in |

## Environment variables — API

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | Yes | `development` / `staging` / `production` |
| `SECRET_KEY` | Yes | JWT signing key (32+ random bytes) |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://...` |
| `REDIS_URL` | Yes | `redis://...` |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `SMS_PROVIDER` | Prod | `msg91` / `twilio` / `mock` |
| `MSG91_AUTH_KEY` | Prod | MSG91 API key |
| `S3_ENDPOINT` | Yes | S3/R2 endpoint URL |
| `S3_ACCESS_KEY` | Yes | Storage access key |
| `S3_SECRET_KEY` | Yes | Storage secret |
| `S3_BUCKET` | Yes | Bucket name |
| `S3_PUBLIC_URL` | Yes | CDN base URL for images |

## Environment variables — Web

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Public API base URL |

## Docker build — API

```bash
cd api
docker build -t carmarket-api:latest .
docker run -p 8000:8000 --env-file .env carmarket-api:latest
```

## Database migrations (production)

```bash
alembic upgrade head
```

Never modify production schema manually.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`):
- On push/PR to `main`: API tests, web lint + build
- Production deploy: add deploy workflow when hosting is chosen

## Production checklist

- [ ] Strong `SECRET_KEY` generated and stored in secrets manager
- [ ] Managed PostgreSQL with backups + PITR
- [ ] Managed Redis
- [ ] S3/R2 bucket with CORS for presigned uploads
- [ ] HTTPS everywhere (TLS termination at LB)
- [ ] Rate limiting enabled
- [ ] SMS provider configured and tested
- [ ] CORS locked to production domains
- [ ] Structured logging → log aggregator
- [ ] Error monitoring (Sentry or similar)
- [ ] Privacy policy URL live
- [ ] Account deletion tested

## Rollback procedure

1. Revert deployment to previous container/image tag
2. If migration was applied: run `alembic downgrade -1` only if backward-compatible
3. Verify `/health/ready` returns 200
4. Monitor error rates for 15 minutes

## Recommended hosting (not finalized)

| Component | Option A | Option B |
|-----------|----------|----------|
| API | Fly.io | AWS ECS |
| Web | Vercel | Cloudflare Pages |
| DB | Neon / Supabase | AWS RDS |
| Redis | Upstash | ElastiCache |
| Storage | Cloudflare R2 | AWS S3 + CloudFront |
