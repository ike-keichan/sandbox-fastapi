import pytest_asyncio
import starlette.status
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.db import Base, get_db
from api.main import app

# 接続するデータベースのURL。
# DBはSQLite、ドライバにaiosqliteを使用。
ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    # DB接続用の非同期エンジン
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

    # 非同期セッション
    async_session = async_sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # テスト用にDBをリセット
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # テスト用に非同期にデータベースセッションを応答
    async def get_test_db():
        async with async_session() as session:
            yield session

    # テスト用にDBの向き先を変更
    app.dependency_overrides[get_db] = get_test_db

    # テスト用に非同期HTTPクライアントを応答
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    # テスト用の設定を元に戻す
    app.dependency_overrides.clear()
    await async_engine.dispose()


async def test_hello(async_client):
    response = await async_client.get("/hello")
    assert response.status_code == starlette.status.HTTP_200_OK
    assert response.json() == {"message": "hello world!"}
