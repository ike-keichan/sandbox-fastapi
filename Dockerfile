FROM python:3.15-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /src

# コンテナは、手元のパソコンと同じユーザーで動かす（docker-compose.yaml の user を参照）。
# どのユーザーでも動くように、設定は、ユーザーごとのファイルではなく、環境変数で行う。
# - HOME: Poetry などが、設定やキャッシュを置く場所。誰でも書き込める /tmp にする。
# - POETRY_VIRTUALENVS_IN_PROJECT: 仮想環境を、プロジェクトの中（/src/.venv）に作る。
# - USER: ユーザーの名前。手元のユーザーの番号は、コンテナの中では、名前を持たない。
#   名前を調べるライブラリ（aiomysql）が、読み込みの時点で失敗するので、名前を決めておく。
ENV HOME=/tmp \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    USER=app

# パッケージ管理の Poetry を入れる。
# パッケージそのものは、イメージには入れない。docker-compose.yaml で /src/.venv にフォルダを割り当てていて、
# そこに make setup（または make py/install）で入れる。
RUN pip install --no-cache-dir poetry==2.5.1

CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload", "--reload-dir", "api"]
