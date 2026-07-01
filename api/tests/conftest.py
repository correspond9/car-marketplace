import asyncio
import os
from collections.abc import AsyncGenerator, Generator

os.environ.setdefault("SECRET_KEY", "test-secret-key-minimum-32-characters-long")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("SMS_PROVIDER", "mock")
os.environ["S3_ACCESS_KEY"] = ""
os.environ["S3_SECRET_KEY"] = ""
os.environ["S3_ENDPOINT"] = ""

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure import redis_client
from app.infrastructure.database import Base, UserModel, get_db_session
from app.main import app
from app.domain.enums import UserRole
from app.core.security import normalize_phone
from sqlalchemy import select

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def fake_redis() -> AsyncGenerator[None, None]:
    redis_client._redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield
    if redis_client._redis_client is not None:
        await redis_client._redis_client.aclose()
    redis_client._redis_client = None


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
        await db_session.commit()

    app.dependency_overrides[get_db_session] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    phone = "9876543210"
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    response = await client.post(
        "/api/v1/auth/otp/verify", json={"phone": phone, "otp": "123456"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def moderator_headers(
    client: AsyncClient, db_session: AsyncSession
) -> dict[str, str]:
    phone = "9988776655"
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    response = await client.post(
        "/api/v1/auth/otp/verify", json={"phone": phone, "otp": "123456"}
    )
    token = response.json()["access_token"]
    normalized = normalize_phone(phone)
    result = await db_session.execute(select(UserModel).where(UserModel.phone == normalized))
    user = result.scalar_one()
    user.role = UserRole.MODERATOR
    await db_session.flush()
    return {"Authorization": f"Bearer {token}"}
