from httpx import AsyncClient


async def test_create_note(async_client_test: AsyncClient, setup_user):
    response = await async_client_test.post(
        "/auth/token/", data={"username": "string", "password": "string"}
    )
    token = response.json().get("access_token")

    response = await async_client_test.post(
        "/notes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Note", "content": "This is a test note"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"


async def test_read_notes(async_client_test: AsyncClient, setup_user):
    # Create a note first
    response = await async_client_test.post(
        "/auth/token/", data={"username": "string", "password": "string"}
    )
    token = response.json().get("access_token")

    await async_client_test.post(
        "/notes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Test Note", "content": "This is a test note"},
    )

    response = await async_client_test.get(
        "/notes/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    notes = response.json()
    assert len(notes) > 0
    assert notes[0]["title"] == "Test Note"
    assert notes[0]["content"] == "This is a test note"
