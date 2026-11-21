from sqlalchemy import create_engine

from api.db import build_db_url
from api.models.task.index import Base

# 接続するデータベースのURL。
# DBはMySQL、ドライバにpymysqlを使用。
DB_URL = build_db_url("pymysql")

# DB接続用のエンジン
engine = create_engine(DB_URL, echo=True)


def reset_database():
    """
    DBをリセットする関数。
    現在のDBの全テーブルを削除し、再度作成する。
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()
