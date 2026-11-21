import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# DBの接続先。環境変数で上書きできる（docker-compose.yaml を参照）。
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "demo")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def build_db_url(driver: str) -> str:
    """
    接続するデータベースのURLを組み立てる関数。

    Args:
        driver (str): 使用するドライバ。非同期の処理は"aiomysql"、同期の処理は"pymysql"。

    Returns:
        str: データベースのURL。
    """
    credential = f"{DB_USER}:{DB_PASSWORD}" if DB_PASSWORD else DB_USER
    return f"mysql+{driver}://{credential}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"


# 接続するデータベースのURL。
# DBはMySQL、ドライバにaiomysqlを使用。
ASYNC_DB_URL = build_db_url("aiomysql")

# DB接続用の非同期エンジン
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

# 非同期セッション
async_session = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


class Base(DeclarativeBase):
    """
    全モデルの基底クラス。
    """


async def get_db():
    """
    非同期にデータベースセッションを応答する関数。
    """
    async with async_session() as session:
        yield session
