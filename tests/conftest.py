from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import api.models  # noqa: F401
from api.db import Base, get_db
from api.main import app

# テストで接続するデータベースのURL。
# DBはメモリ上のSQLite、ドライバにaiosqliteを使用。
ASYNC_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """
    テスト用のHTTPクライアントを応答するフィクスチャ。
    テストごとに、空のDBから始まる。
    """
    # DB接続用の非同期エンジン
    async_engine = create_async_engine(ASYNC_DB_URL)

    # 非同期セッション
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)

    # テスト用のDBに、テーブルを作成
    async with async_engine.begin() as conn:
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
