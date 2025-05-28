import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def clean_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        yield client
        await client.aclose()


@pytest.mark.asyncio
async def test_two_post_auth1(clean_client):
    token_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    user_response = await clean_client.get(
        "/auth/read_current_user", headers={"Authorization": f"Bearer {token}"}
    )
    assert user_response.status_code == 200


@pytest.mark.asyncio
async def test_three_get_id_tasks(clean_client):
    clean_client.headers.clear()
    clean_client.cookies.clear()

    response = await clean_client.get("/tasks/2")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        pass
    elif response.status_code == 404:
        assert response.json()["detail"] == "Tasks not found!"


@pytest.mark.asyncio
async def test_four_post_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "test222",
        "description": "test",
        "status": "active",
        "user_id": 12,
    }
    response = await clean_client.post(
        "/tasks/", json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "This name already exists or the id was not found or invalid"
    )


@pytest.mark.asyncio
async def test_five_post_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "apple22",
        "description": "prive 50",
        "status": "22",
        "user_id": 12,
    }
    response = await clean_client.post(
        "/tasks/", json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid status"


@pytest.mark.asyncio
async def test_six_post_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "apple23",
        "description": "     ",
        "status": "new",
        "user_id": 12,
    }
    response = await clean_client.post(
        "/tasks/", json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid description"


@pytest.mark.asyncio
async def test_seven_post_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "apple24",
        "description": "price 100",
        "status": "new",
        "user_id": 12,
    }
    response = await clean_client.post(
        "/tasks/", json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "This ID is already taken by another user or does not exist"
    )


@pytest.mark.asyncio
async def test_eight_put_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "test222",
        "description": "test",
        "status": "active",
        "user_id": 32,
    }
    response = await clean_client.put(
        "/tasks/", params={"task_id": 9}, json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "This name already exists or the id was not found or invalid"
    )


@pytest.mark.asyncio
async def test_nine_put_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "apple22",
        "description": "prive 50",
        "status": "22",
        "user_id": 12,
    }
    response = await clean_client.put(
        "/tasks/", params={"task_id": 9}, json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid status"


@pytest.mark.asyncio
async def test_ten_put_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "apple23",
        "description": "     ",
        "status": "new",
        "user_id": 12,
    }
    response = await clean_client.put(
        "/tasks/", params={"task_id": 9}, json=json_data, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid description"


@pytest.mark.asyncio
async def test_eleven_put_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    json_data = {
        "title": "apple24412",
        "description": "price 100",
        "status": "new",
        "user_id": 20,
    }
    response = await clean_client.put(
        "/tasks/", params={"task_id": 9}, json=json_data, headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "ID does not exist or is busy!"


@pytest.mark.asyncio
async def test_twelve_delete_tasks(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await clean_client.delete(
        "/tasks/", params={"task_id": 9}, headers=headers
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "ID not found!"


@pytest.mark.asyncio
async def test_thirteen_get_user(clean_client):
    response = await clean_client.get("/users/user/35")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found!"


@pytest.mark.asyncio
async def test_fiveteen_put_users(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    tdata = {
        "name": "frensski",
        "email": "frensski01@gmail.com",
        "password": "12345gmail",
    }

    response = await clean_client.put(
        "/users/", params={"user_id": 9}, json=tdata, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid name or already in use"


@pytest.mark.asyncio
async def test_sixteen_put_users(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    tdata = {
        "name": "frensski3451",
        "email": "frensski@mail.ru",
        "password": "12345gmail",
    }

    response = await clean_client.put(
        "/users/", params={"user_id": 9}, json=tdata, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid email or already in use"


@pytest.mark.asyncio
async def test_seventeen_put_users(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    tdata = {
        "name": "frensski3832",
        "email": "frensski0154@gmail.com",
        "password": "      ",
    }

    response = await clean_client.put(
        "/users/", params={"user_id": 9}, json=tdata, headers=headers
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid password"


@pytest.mark.asyncio
async def test_eighteen_put_users(clean_client):
    login_response = await clean_client.post(
        "/auth/token", data={"username": "frensski", "password": "123gmail"}
    )
    assert (
        login_response.status_code == 200
    ), f"Login failed: {login_response.text}"
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    tdata = {
        "name": "frensski",
        "email": "frensski01@gmail.com",
        "password": "12345gmail",
    }

    response = await clean_client.put(
        "/users/", params={"user_id": 33}, json=tdata, headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot delete someone else's user"


@pytest.mark.asyncio
async def test_nineteen_put_users(clean_client):
    tdata = {
        "name": "frensski",
        "email": "frensski01@gmail.com",
        "password": "12345gmail",
    }

    response = await clean_client.post("/auth/", json=tdata)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid name or already in use"


@pytest.mark.asyncio
async def test_twenty_put_users(clean_client):
    tdata = {
        "name": "frensski54f77",
        "email": "frensski@gmail.com",
        "password": "12345gmail",
    }

    response = await clean_client.post("/auth/", json=tdata)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email or already in use"


@pytest.mark.asyncio
async def test_twenty_one_put_users(clean_client):
    tdata = {
        "name": "frensski3331",
        "email": "frensski6453@gmail.com",
        "password": "      ",
    }

    response = await clean_client.post("/auth/", json=tdata)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid password"
