import sys

from sqlalchemy import MetaData, create_engine

# テーブルを作るには、モデルを読み込んでおく必要がある。
# モデルは api/models/__init__.py でまとめて読み込んでいる。
import api.models  # noqa: F401
from api.db import DB_ECHO, Base, build_db_url

# DB接続用のエンジン
# DBはMySQL、ドライバにpymysqlを使用。この処理は1回実行して終わるので、同期のエンジンを使う。
engine = create_engine(build_db_url("pymysql"), echo=DB_ECHO)


def create_tables() -> None:
    """
    まだ存在しないテーブルを作成する関数。
    すでにあるテーブルとデータは、そのまま残る。
    """
    Base.metadata.create_all(bind=engine)


def reset_database() -> None:
    """
    DBをリセットする関数。
    DBにある全テーブルを削除し、再度作成する。データは消える。
    """
    # DBにあるテーブルを調べてから削除する。
    # こうすると、モデルを消したり名前を変えたりして残った、古いテーブルも消せる。
    existing = MetaData()
    existing.reflect(bind=engine)
    existing.drop_all(bind=engine)
    create_tables()


if __name__ == "__main__":
    if "--reset" in sys.argv[1:]:
        reset_database()
        print("Reset the database")
    else:
        create_tables()
        print("Created the tables")
