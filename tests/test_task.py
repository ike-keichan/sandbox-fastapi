import pytest
from httpx import AsyncClient
from starlette import status

from api.models.task.index import TITLE_MAX_LENGTH


async def create_task(async_client: AsyncClient, **task_input: object) -> dict:
    """
    テスト用に、タスクを1件作って、レスポンスの中身を応答する関数。
    """
    response = await async_client.post("/tasks", json={"title": "テストタスク", **task_input})
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()


async def test_create(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/tasks", json={"title": "テストタスク", "due_date": "2024-09-01"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": 1,
        "title": "テストタスク",
        "due_date": "2024-09-01",
        "is_done": False,
    }


async def test_create_without_due_date(async_client: AsyncClient) -> None:
    task = await create_task(async_client)
    assert task["due_date"] is None


@pytest.mark.parametrize(
    "task_input",
    [
        {},
        {"title": ""},
        {"title": None},
        {"title": 123},
        {"title": "あ" * (TITLE_MAX_LENGTH + 1)},
        {"title": "テストタスク", "due_date": "2024-12-32"},
        {"title": "テストタスク", "due_date": "2024/12/01"},
        {"title": "テストタスク", "due_date": "2024-1201"},
    ],
)
async def test_create_with_invalid_input(async_client: AsyncClient, task_input: dict) -> None:
    response = await async_client.post("/tasks", json=task_input)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 不正な入力では、タスクが作られない。
    response = await async_client.get("/tasks")
    assert response.json() == []


async def test_create_with_longest_title(async_client: AsyncClient) -> None:
    task = await create_task(async_client, title="あ" * TITLE_MAX_LENGTH)
    assert len(task["title"]) == TITLE_MAX_LENGTH


async def test_get(async_client: AsyncClient) -> None:
    task = await create_task(async_client)

    response = await async_client.get(f"/tasks/{task['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == task


async def test_list(async_client: AsyncClient) -> None:
    first = await create_task(async_client, title="1つ目")
    second = await create_task(async_client, title="2つ目")

    response = await async_client.get("/tasks")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [first, second]


async def test_list_filtered_by_is_done(async_client: AsyncClient) -> None:
    done = await create_task(async_client, title="完了するタスク")
    not_done = await create_task(async_client, title="未完了のタスク")
    done = (await async_client.put(f"/tasks/{done['id']}/done")).json()

    response = await async_client.get("/tasks", params={"is_done": "true"})
    assert response.json() == [done]

    response = await async_client.get("/tasks", params={"is_done": "false"})
    assert response.json() == [not_done]


async def test_list_with_invalid_is_done(async_client: AsyncClient) -> None:
    response = await async_client.get("/tasks", params={"is_done": "abc"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_update(async_client: AsyncClient) -> None:
    task = await create_task(async_client, due_date="2024-09-01")

    response = await async_client.put(f"/tasks/{task['id']}", json={"title": "更新したタスク"})
    assert response.status_code == status.HTTP_200_OK
    # 渡さなかった期日は、空になる（PUTは、全体を置き換える）。
    assert response.json() == {**task, "title": "更新したタスク", "due_date": None}

    response = await async_client.get(f"/tasks/{task['id']}")
    assert response.json()["title"] == "更新したタスク"


async def test_update_with_invalid_input(async_client: AsyncClient) -> None:
    task = await create_task(async_client)

    response = await async_client.put(f"/tasks/{task['id']}", json={"title": ""})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # 不正な入力では、タスクが変わらない。
    response = await async_client.get(f"/tasks/{task['id']}")
    assert response.json() == task


async def test_delete(async_client: AsyncClient) -> None:
    task = await create_task(async_client)

    response = await async_client.delete(f"/tasks/{task['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    response = await async_client.get(f"/tasks/{task['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_done(async_client: AsyncClient) -> None:
    task = await create_task(async_client)

    # 完了にする
    response = await async_client.put(f"/tasks/{task['id']}/done")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {**task, "is_done": True}

    # もう一度呼んでも、完了のまま
    response = await async_client.put(f"/tasks/{task['id']}/done")
    assert response.json()["is_done"] is True

    # 未完了に戻す
    response = await async_client.delete(f"/tasks/{task['id']}/done")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {**task, "is_done": False}


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/tasks/999"),
        ("PUT", "/tasks/999"),
        ("DELETE", "/tasks/999"),
        ("PUT", "/tasks/999/done"),
        ("DELETE", "/tasks/999/done"),
    ],
)
async def test_not_found(async_client: AsyncClient, method: str, path: str) -> None:
    json = {"title": "テストタスク"} if method == "PUT" and not path.endswith("/done") else None
    response = await async_client.request(method, path, json=json)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Task not found"}


async def test_task_id_must_be_integer(async_client: AsyncClient) -> None:
    response = await async_client.get("/tasks/abc")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
