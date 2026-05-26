import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.deps import get_db
from app.main import app

engine = create_async_engine(settings.db_url, poolclass=NullPool)


@pytest_asyncio.fixture
async def client():
    async with engine.connect() as conn:
        await conn.begin()

        session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

        app.dependency_overrides.clear()
        await session.close()
        await conn.rollback()
