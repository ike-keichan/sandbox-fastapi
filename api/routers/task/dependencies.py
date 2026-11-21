from typing import Annotated

from fastapi import Depends, HTTPException, status

import api.cruds.task.index as task_crud
import api.models.task.index as task_model
from api.db import DbSession


async def find_task(task_id: int, db: DbSession) -> task_model.Task:
    """
    パスの task_id からタスクを取得する関数。存在しない場合は、404を応答する。

    1件のタスクを対象にするAPIは、どれも最初にこの処理が必要になる。
    ルーターごとに書かずに済むように、ここにまとめている。
    """
    task = await task_crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


# ルーターの引数に書く、対象のタスクの型。
# 例: async def get_task(task: TargetTask) -> task_model.Task:
TargetTask = Annotated[task_model.Task, Depends(find_task)]
