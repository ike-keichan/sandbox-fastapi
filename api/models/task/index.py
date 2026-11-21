import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from api.db import Base

# タスク名の長さの上限。リクエストの検査（schemas）でも、同じ値を使う。
TITLE_MAX_LENGTH = 1024


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    due_date: Mapped[datetime.date | None]
    is_done: Mapped[bool] = mapped_column(default=False)
