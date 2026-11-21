from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.db import async_engine
from api.routers.hello import index as hello
from api.routers.task import index as task


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """
    アプリケーションの起動時と終了時の処理。
    終了時に、データベースへの接続を閉じる。
    """
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)

# 機能を足したら、ここにルーターを登録する。
app.include_router(hello.router)
app.include_router(task.router)
app.include_router(task.router)
