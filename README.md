# CarMarket — India Used Car Marketplace

Production-grade peer-to-peer and dealer marketplace for used cars in India.

## Surfaces

| App | Stack | Path |
|-----|-------|------|
| API | Python 3.12, FastAPI, PostgreSQL, Redis | `api/` |
| Web | Next.js 15, TypeScript, Tailwind CSS | `web/` |
| **Android app** | Kotlin + Jetpack Compose — login, home, search, detail | `android/` |
| **iOS app** | Swift + SwiftUI — login, home, search, detail | `ios/CarMarket.xcodeproj` |

## Quick start

```bash
# Start infrastructure
docker compose up -d

# API
cd api && python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Web
cd web && npm install && npm run dev
```

- API docs: http://localhost:8000/docs
- Web: http://localhost:3000

See [docs/SETUP.md](docs/SETUP.md) for full setup and [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for production.

## Documentation

All project documentation lives in [`docs/`](docs/). Start with [PROJECT_STATUS.md](docs/PROJECT_STATUS.md) and [HANDOFF.md](docs/HANDOFF.md).

## License

Proprietary — all rights reserved.
