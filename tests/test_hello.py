from httpx import AsyncClient
from starlette import status


async def test_hello(async_client: AsyncClient) -> None:
    response = await async_client.get("/hello")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "hello world!"}


async def test_not_found(async_client: AsyncClient) -> None:
    response = await async_client.get("/unknown")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not Found"}
