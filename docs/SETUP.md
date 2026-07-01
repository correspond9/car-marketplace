# Setup Guide

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.12+ |
| Node.js | 20 LTS+ |
| Docker Desktop | Latest |
| Git | Latest |

Optional for public mobile):
- Android Studio (Ladybug+)
- Xcode 16+ (macOS only)

## 1. Clone and infrastructure

```bash
git clone <repo-url> Cars-Marketplace-Apps
cd Cars-Marketplace-Apps
docker compose up -d
```

Services started:
- PostgreSQL → `localhost:5432` (user/pass/db: `carmarket`)
- Redis → `localhost:6379`
- MinIO → `localhost:9000` (console `9001`, user/pass: `minioadmin`)

## 2. API setup

```bash
cd api
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Verify: http://localhost:8000/health

### Dev OTP

In development (`APP_ENV=development`), any phone number works with OTP **`123456`**.

## 3. Web setup

```bash
cd web
npm install
copy .env.example .env.local
npm run dev
```

Verify: http://localhost:3000

## 4. Running tests

```bash
# API
cd api && pytest -v

# Web
cd web && npm run lint && npm run build
```

## 5. Mobile (optional)

### Android

Open `android/` in Android Studio → Sync Gradle → Run on emulator.

Set API base URL in `android/app/src/main/java/in/carmarket/app/data/ApiConfig.kt`.

### iOS

Open `ios/CarMarket.xcodeproj` in Xcode → Run on simulator.

Set API base URL in `ios/CarMarket/Config/ApiConfig.swift`.

## Environment files

| File | Purpose |
|------|---------|
| `api/.env` | API secrets (from `.env.example`) |
| `web/.env.local` | Public API URL for Next.js |

Never commit real `.env` files.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| DB connection refused | Ensure `docker compose up -d` and port 5432 free |
| Alembic errors | Drop volume: `docker compose down -v` (dev only) |
| CORS errors | Check `CORS_ORIGINS` in `api/.env` includes web URL |
