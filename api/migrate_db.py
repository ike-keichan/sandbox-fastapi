from sqlalchemy import create_engine

# テーブルを作るには、モデルを読み込んでおく必要がある。
# モデルを追加したら、ここで読み込む。
# 例: import api.models.task.index  # noqa: F401
from api.db import Base, build_db_url

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
