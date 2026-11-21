import datetime

from pydantic import BaseModel, ConfigDict, Field


class Task(BaseModel):
    id: int
    title: str | None = Field(None, examples=["ラジオ体操"], description="タスク名")
    due_date: datetime.date | None = Field(None, examples=["2024-09-01"], description="期日")
    is_done: bool = Field(False, description="完了状態の真偽値")

    model_config = ConfigDict(from_attributes=True)


class TaskInput(BaseModel):
    title: str | None = Field(None, examples=["ラジオ体操"], description="タスク名")
    due_date: datetime.date | None = Field(None, examples=["2024-09-01"], description="期日")
