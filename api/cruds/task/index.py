from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import api.models.task.index as task_model
import api.schemas.task.index as task_schema


async def create_task(db: AsyncSession, task_input: task_schema.TaskInput) -> task_model.Task:
    """
    タスクの新規作成

    Args:
        db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
        task_input (task_schema.TaskInput): 新規作成するタスクの内容。

    Returns:
        task_model.Task: 新規作成したタスクのオブジェクト。
    """
    task = task_model.Task(**task_input.model_dump())
    db.add(task)
    await db.commit()
    return task


async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
    """
    タスクの取得

    Args:
        db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
        task_id (int): 取得したいタスクのID。

    Returns:
        task_model.Task | None: 指定されたIDのタスクのオブジェクト。存在しない場合はNone。
    """
    return await db.get(task_model.Task, task_id)


async def get_tasks(db: AsyncSession, is_done: bool | None) -> list[task_model.Task]:
    """
    タスク一覧の取得

    Args:
        db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
        is_done (bool | None): フィルタリング条件となるタスクの完了状態。Noneの場合は絞り込まない。

    Returns:
        list[task_model.Task]: タスクのオブジェクトのリスト。IDの小さい順。
    """
    statement = select(task_model.Task).order_by(task_model.Task.id)
    if is_done is not None:
        statement = statement.where(task_model.Task.is_done == is_done)

    result = await db.scalars(statement)
    return list(result.all())


async def update_task(
    db: AsyncSession,
    task: task_model.Task,
    task_input: task_schema.TaskInput,
) -> task_model.Task:
    """
    タスクの更新

    Args:
        db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
        task (task_model.Task): 更新対象のタスクのオブジェクト。
        task_input (task_schema.TaskInput): 更新する内容。

    Returns:
        task_model.Task: 更新したタスクのオブジェクト。
    """
    task.title = task_input.title
    task.due_date = task_input.due_date
    await db.commit()
    return task


async def delete_task(db: AsyncSession, task: task_model.Task) -> None:
    """
    タスクの削除

    Args:
        db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
        task (task_model.Task): 削除するタスクのオブジェクト。
    """
    await db.delete(task)
    await db.commit()
