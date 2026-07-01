# Testing

## Strategy

| Layer | Tool | Scope |
|-------|------|-------|
| Unit | pytest | Domain logic, services, utilities |
| Integration | pytest + test DB | Repositories, API routes |
| API contract | pytest + OpenAPI | Response shapes |
| Web | ESLint + build | Type safety, compile |
| E2E | Playwright (planned) | Critical user flows |
| Mobile | JUnit / XCTest (planned) | ViewModels, API clients |

## Running API tests

```bash
cd api
pip install -e ".[dev]"
pytest -v --cov=app --cov-report=term-missing
```

Tests use a separate PostgreSQL database or SQLite for unit tests where applicable. Integration tests require Docker Postgres or `TEST_DATABASE_URL`.

## Test structure

```
api/tests/
├── conftest.py          # Fixtures: client, db, auth headers
├── unit/
│   ├── test_security.py
│   └── test_listing_service.py
└── integration/
    ├── test_auth.py
    ├── test_listings.py
    └── test_health.py
```

## Coverage targets

| Module | Target |
|--------|--------|
| Auth | 90%+ |
| Listings | 85%+ |
| Search | 80%+ |
| Overall | 80%+ |

## CI

GitHub Actions runs on every push/PR:
- `pytest` with coverage threshold check
- `ruff check` + `mypy` (API)
- `npm run lint` + `npm run build` (web)

## Manual QA checklist (MVP)

- [ ] OTP login with valid/invalid codes
- [ ] Create listing draft → publish → appears in search
- [ ] Masked registration number on public detail
- [ ] Unauthorized user cannot edit others' listings
- [ ] Moderator can approve/reject pending listing
- [ ] Rate limit triggers on repeated OTP requests
- [ ] Account deletion removes PII

## Edge cases to test

- Publish listing without required fields → 422
- Expired OTP → 401
- Search with no results → empty array, 200
- Duplicate phone registration → login existing user
- Dealer store slug collision → 409
