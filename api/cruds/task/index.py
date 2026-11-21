from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

import api.models.task.index as task_model
import api.schemas.task.index as task_schema


async def create_task(db: AsyncSession, new_task: task_schema.TaskInput) -> task_model.Task:
    """
    タスクの新規作成

    Args:
        db (Session): SQLAlchemyのデータベースセッションオブジェクト。
        new_task (task_schema.TaskInput): 新規作成するタスクのオブジェクト。

    Returns:
        task_model.Task: 新規作成したタスクのオブジェクト。
    """
    task = task_model.Task(**new_task.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> task_model.Task | None:
    """
    タスクの取得

    Args:
        db (Session): SQLAlchemyのデータベースセッションオブジェクト。
        task_id (int): 取得したいタスクのID。

    Returns:
        Optional[task_model.Task]: 指定されたIDのタスクのオブジェクト。存在しない場合はNone。
    """
    result: Result = await db.execute(select(task_model.Task).filter(task_model.Task.id == task_id))
    return result.scalars().first()


async def get_tasks(db: AsyncSession, is_done: bool | None) -> list[task_model.Task]:
    """
    タスク一覧の取得

    Args:
        db (Session): SQLAlchemyのデータベースセッションオブジェクト。
        is_done (Optional[bool]): フィルタリング条件となるタスクの完了状態。

    Returns:
        List[task_model.Task]: タスクのオブジェクトのリスト
    """
    result: Result = await db.execute(
        select(task_model.Task).filter(
            task_model.Task.is_done == is_done if is_done is not None else True
        )
    )
    return list(result.scalars().all())


async def update_task(
    db: AsyncSession,
    update_task: task_schema.TaskInput,
    target_task: task_model.Task,
) -> task_model.Task:
    """
    タスクの更新

    Args:
        db (Session): SQLAlchemyのデータベースセッションオブジェクト。
        update_task (task_schema.TaskInput): 更新するタスクのオブジェクト。
        target_task (task_schema.Task): 更新対象のタスクのオブジェクト。

    Returns:
        task_model.Task: 更新したタスクのオブジェクト。
    """
    target_task.title = update_task.title
    target_task.due_date = update_task.due_date
    db.add(target_task)
    await db.commit()
    await db.refresh(target_task)
    return target_task


async def delete_task(db: AsyncSession, delete_task: task_model.Task) -> None:
    """
    タスクの削除

    Args:
        db (Session): SQLAlchemyのデータベースセッションオブジェクト。
        delete_task (task_model.Task): 削除するタスクのオブジェクト。

    Returns:
        None: この関数は値を返しません。
    """
    await db.delete(delete_task)
    await db.commit()
