from fastapi import FastAPI

from api.routers.hello import index as hello

app = FastAPI()

app.include_router(hello.router)
