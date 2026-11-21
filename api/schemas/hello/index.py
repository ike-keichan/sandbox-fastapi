from pydantic import BaseModel, Field


class Hello(BaseModel):
    message: str = Field(examples=["hello world!"], description="メッセージ")
