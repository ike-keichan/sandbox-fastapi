from sqlalchemy.ext.asyncio import AsyncSession

import api.models.task.index as task_model


async def change_is_done(db: AsyncSession, task: task_model.Task, is_done: bool) -> task_model.Task:
    """
    タスクの完了状態の更新

    Args:
        db (AsyncSession): SQLAlchemyのデータベースセッションオブジェクト。
        task (task_model.Task): 更新対象のタスクのオブジェクト。
        is_done (bool): 更新後の完了状態。

    Returns:
        task_model.Task: 更新したタスクのオブジェクト。
    """
    task.is_done = is_done
    await db.commit()
    return task
