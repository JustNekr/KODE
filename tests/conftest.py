from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from config import settings
from database import Base, get_async_session
from main import app


@pytest.fixture(scope="function")
async def async_session_maker_test():
    database_url_test = (
        f"{settings.db_engine}://{settings.db_user_test}:{settings.db_pass_test}@"
        f"{settings.db_host_test}:{settings.db_port_test}/{settings.db_name_test}"
    )

    engine_test = create_async_engine(database_url_test)
    async_session_maker_test = async_sessionmaker(
        bind=engine_test, class_=AsyncSession, expire_on_commit=False
    )

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield async_session_maker_test


@pytest.fixture(scope="function")
async def async_client_test(async_session_maker_test):
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_maker_test() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="function")
async def setup_user(async_client_test: AsyncClient):
    response = await async_client_test.post(
        "/auth/user/", json={"username": "string", "password": "string"}
    )
    assert response.status_code == 200
