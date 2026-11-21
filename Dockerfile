FROM python:3.15-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /src

# パッケージ管理の Poetry を入れる。仮想環境は、プロジェクトの中（/src/.venv）に作る設定にする。
# パッケージそのものは、イメージには入れない。docker-compose.yaml で /src/.venv にフォルダを割り当てていて、
# そこに make setup（または make py/install）で入れる。
RUN pip install --no-cache-dir poetry==2.5.1 \
    && poetry config virtualenvs.in-project true

CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--reload", "--reload-dir", "api"]
