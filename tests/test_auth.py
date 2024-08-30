from httpx import AsyncClient


async def test_create_user(async_client_test: AsyncClient):
    response = await async_client_test.post(
        "/auth/user/", json={"username": "string", "password": "string"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "string"


async def test_create_user_existing_username(
    async_client_test: AsyncClient, setup_user
):
    response = await async_client_test.post(
        "/auth/user/", json={"username": "string", "password": "string"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


async def test_get_token(async_client_test: AsyncClient, setup_user):
    response = await async_client_test.post(
        "/auth/token/", data={"username": "string", "password": "string"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_login_invalid_credentials(async_client_test: AsyncClient):
    response = await async_client_test.post(
        "/auth/token/",
        data={"username": "incorrect_username", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
