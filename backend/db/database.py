from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        if settings.DATABASE_URL.startswith("sqlite"):
            from sqlalchemy import inspect, text
            columns = await conn.run_sync(
                lambda sync_conn: {column["name"] for column in inspect(sync_conn).get_columns("analysis_reports")}
            )
            if "requirement_coverage" not in columns:
                await conn.execute(text("ALTER TABLE analysis_reports ADD COLUMN requirement_coverage VARCHAR"))
            if "overall_match_percent" not in columns:
                await conn.execute(text("ALTER TABLE analysis_reports ADD COLUMN overall_match_percent INTEGER"))
