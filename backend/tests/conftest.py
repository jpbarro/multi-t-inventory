import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.database import get_db, Base
from app.main import app

# 1. DATABASE SETUP
# Use a separate DB for tests to avoid wiping your dev data!
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/test_db"

# NullPool is important here: it prevents the engine from holding 
# connections open, which can lock the DB during test teardowns.
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Creates tables once before all tests, drops them after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 2. SESSION FIXTURE (The Rollback Strategy)
@pytest.fixture(scope="function")
async def db_session():
    """
    Creates a fresh sqlalchemy session for each test that rolls back 
    changes after the test finishes.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()

# 3. APP FIXTURE (The Override)
@pytest.fixture(scope="function")
async def client(db_session):
    """
    Overrides the get_db dependency with our testing session
    and returns an AsyncClient.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()