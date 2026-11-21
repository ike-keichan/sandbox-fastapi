from fastapi import APIRouter

import api.cruds.task.done as done_crud
import api.models.task.index as task_model
import api.schemas.task.index as task_schema
from api.db import DbSession
from api.routers.task.dependencies import TargetTask

# パスの前半（/tasks）とタグは、取り込む側の routers/task/index.py で付けている。
router = APIRouter()


# タスクを完了にする
# 何度呼んでも結果が同じになるように、「切り替え」ではなく「完了にする」にしている。
@router.put("/{task_id}/done", response_model=task_schema.Task)
async def mark_task_as_done(task: TargetTask, db: DbSession) -> task_model.Task:
    return await done_crud.change_is_done(db, task, is_done=True)


# タスクを未完了に戻す
@router.delete("/{task_id}/done", response_model=task_schema.Task)
async def mark_task_as_not_done(task: TargetTask, db: DbSession) -> task_model.Task:
    return await done_crud.change_is_done(db, task, is_done=False)
