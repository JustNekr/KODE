from httpx import AsyncClient


async def test_create_user(async_client_test: AsyncClient):
    response = await async_client_test.post(
        "/auth/user/", json={"username": "string", "password": "string"}
    )
    print(response.json())
    assert response.status_code == 200


async def test_get_token(async_client_test: AsyncClient, setup_user):
    response = await async_client_test.post(
        "/auth/token/", json={"username": "string", "password": "string"}
    )
    assert response.status_code == 200
