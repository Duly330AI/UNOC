"""
Database Connection - Simple and Clean
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://unoc:unocpw@localhost:5432/unocdb",
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    future=True,
)

# Session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database - Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes.
    
    Usage:
        @app.get("/devices")
        async def list_devices(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_session_context():
    """
    Context manager for manual session handling.
    
    Usage:
        async with get_session_context() as session:
            result = await session.execute(...)
    """
    async with async_session() as session:
        yield session
