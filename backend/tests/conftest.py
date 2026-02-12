import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.api.deps import get_db
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/test_db"

# 1. Make the Engine a Fixture
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()

# 3. Make the Session Factory a Fixture
@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    return async_sessionmaker(bind=test_engine, expire_on_commit=False)

# 4. Create Tables (Once per session)
@pytest.fixture(scope="session", autouse=True)
async def setup_test_db(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 5. Per-Test Session (Function Scope)
@pytest.fixture(scope="function")
async def db_session(test_session_factory):
    session = test_session_factory()
    yield session
    await session.rollback()
    await session.close()

# 6. The API Client
@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()