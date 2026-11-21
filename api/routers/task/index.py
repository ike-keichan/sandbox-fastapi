from fastapi import APIRouter, status

import api.cruds.task.index as task_crud
import api.models.task.index as task_model
import api.schemas.task.index as task_schema
from api.db import DbSession
from api.routers.task import done
from api.routers.task.dependencies import TargetTask

router = APIRouter(prefix="/tasks", tags=["task"])


# タスク一覧の取得
@router.get("", response_model=list[task_schema.Task])
async def list_tasks(db: DbSession, is_done: bool | None = None) -> list[task_model.Task]:
    return await task_crud.get_tasks(db, is_done)


# タスクの新規作成
@router.post("", response_model=task_schema.Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_input: task_schema.TaskInput, db: DbSession) -> task_model.Task:
    return await task_crud.create_task(db, task_input)


# タスクの取得
@router.get("/{task_id}", response_model=task_schema.Task)
async def get_task(task: TargetTask) -> task_model.Task:
    return task


# タスクの更新
@router.put("/{task_id}", response_model=task_schema.Task)
async def update_task(
    task: TargetTask, task_input: task_schema.TaskInput, db: DbSession
) -> task_model.Task:
    return await task_crud.update_task(db, task, task_input)


# タスクの削除
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task: TargetTask, db: DbSession) -> None:
    await task_crud.delete_task(db, task)


router.include_router(done.router)
