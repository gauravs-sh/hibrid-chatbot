from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/hybrid_rag")

# Support PgBouncer: disable statement cache
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"statement_cache_size": 0}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
