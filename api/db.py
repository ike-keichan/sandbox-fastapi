import os
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# DBの接続先。環境変数で上書きできる（docker-compose.yaml を参照）。
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "demo")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# 実行したSQLをログに出すかどうか。"true" のときだけ出す。
DB_ECHO = os.getenv("DB_ECHO", "false").lower() == "true"


def build_db_url(driver: str) -> URL:
    """
    接続するデータベースのURLを組み立てる関数。

    文字列の連結ではなく URL.create を使う。
    パスワードに "@" や "/" などの記号が入っていても、正しく扱える。

    Args:
        driver (str): 使用するドライバ。非同期の処理は"aiomysql"、同期の処理は"pymysql"。

    Returns:
        URL: データベースのURL。
    """
    return URL.create(
        drivername=f"mysql+{driver}",
        username=DB_USER,
        password=DB_PASSWORD or None,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        query={"charset": "utf8mb4"},
    )


# DB接続用の非同期エンジン
# pool_pre_ping: 接続を使う前に、切れていないかを確かめる。DBを再起動したあとも、エラーにならない。
async_engine = create_async_engine(build_db_url("aiomysql"), echo=DB_ECHO, pool_pre_ping=True)

# 非同期セッション
# expire_on_commit=False: コミットのあとも、取得済みの値をそのまま読めるようにする。
# 非同期の処理では、コミット後に値を読み直そうとするとエラーになるため。
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """
    全モデルの基底クラス。
    """


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
    非同期にデータベースセッションを応答する関数。
    """
    async with async_session() as session:
        yield session


# ルーターの引数に書く、データベースセッションの型。
# 例: async def list_tasks(db: DbSession) -> list[Task]:
DbSession = Annotated[AsyncSession, Depends(get_db)]
