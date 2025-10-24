"""
Test Configuration - Pytest Setup
"""


import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from backend.db import get_session
from backend.main import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# Test session factory
test_async_session = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def async_session():
    """
    Create a fresh database session for each test.
    
    Tables are created before the test and dropped after.
    """
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Yield session
    async with test_async_session() as session:
        yield session
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
def override_get_session(async_session):
    """Override FastAPI dependency for testing"""
    
    async def _override():
        yield async_session
    
    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.clear()
