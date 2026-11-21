from fastapi import APIRouter

import api.schemas.hello.index as hello_schema

router = APIRouter(prefix="/hello", tags=["hello"])


# サンプルのAPI
@router.get("", response_model=hello_schema.Hello)
async def hello() -> hello_schema.Hello:
    return hello_schema.Hello(message="hello world!")
