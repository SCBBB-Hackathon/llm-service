from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from utils.getAPI import getApiKey

DATABASE_URL = getApiKey()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # True면 SQL로그 출력
    pool_size=10,        # 커넥션 풀 사이즈
    max_overflow=20,     # 추가 여유 커넥션
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

# DB 엔진과 세션을 startup에서 생성하므로 함수 형태로 둔다.
def create_engine_and_session():
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return engine, session_factory