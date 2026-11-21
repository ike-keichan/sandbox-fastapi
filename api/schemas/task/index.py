import datetime

from pydantic import BaseModel, ConfigDict, Field

from api.models.task.index import TITLE_MAX_LENGTH


class TaskInput(BaseModel):
    """
    タスクの作成と更新で受け取る項目。利用者が決められる項目だけを持つ。
    """

    title: str = Field(
        min_length=1,
        max_length=TITLE_MAX_LENGTH,
        examples=["ラジオ体操"],
        description="タスク名",
    )
    due_date: datetime.date | None = Field(None, examples=["2024-09-01"], description="期日")


class Task(TaskInput):
    """
    レスポンスで返すタスク。受け取る項目に、サーバーが決める項目を足したもの。
    """

    id: int = Field(description="タスクのID")
    is_done: bool = Field(description="完了状態の真偽値")

    model_config = ConfigDict(from_attributes=True)
