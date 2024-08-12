from http import HTTPStatus

import aiohttp
import pytest_asyncio

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='api_session')
async def api_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='make_get_request')
async def make_get_request(api_session):
    async def inner(url: str, params: dict = None, headers: dict = None):
        full_url = test_settings.service_url + url
        async with api_session.get(full_url, params=params, headers=headers) as response:
            body = await response.json()
            return response, body

    return inner


@pytest_asyncio.fixture(name='make_post_request')
def make_post_request(api_session):
    async def inner(url: str, data: dict = None, headers: dict = None):
        full_url = test_settings.service_url + url
        async with api_session.post(full_url, json=data, headers=headers) as response:
            body = await response.json()
            return response, body

    return inner


@pytest_asyncio.fixture(name='make_put_request')
async def make_put_request(api_session):
    async def inner(url: str, data: dict = None, headers: dict = None):
        full_url = test_settings.service_url + url
        async with api_session.put(full_url, json=data, headers=headers) as response:
            body = await response.json()
            return response, body

    return inner


@pytest_asyncio.fixture(name='make_delete_request')
async def make_delete_request(api_session):
    async def inner(url: str, data: dict = None, headers: dict = None):
        full_url = test_settings.service_url + url
        async with api_session.delete(full_url, json=data, headers=headers) as response:
            body = await response.json()
            return response, body

    return inner


@pytest_asyncio.fixture
async def admin_auth(make_post_request, make_get_request, make_put_request, make_delete_request):
    print('admin_auth1')
    admin_data = {
        "username": "admin",
        "password": "adminpassword"
    }
    response, body = await make_post_request("/api/v1/auth/login", admin_data)
    assert response.status == HTTPStatus.OK, f"Failed to login as admin: {body}"
    admin_token = body["access_token"]
    print(admin_token)

    async def make_authorized_request(method, url, data=None, params=None):
        headers = {"Authorization": f"Bearer {admin_token}"}
        if method == "GET":
            return await make_get_request(url, params=params, headers=headers)
        elif method == "POST":
            return await make_post_request(url, data=data, headers=headers)
        elif method == "PUT":
            return await make_put_request(url, data=data, headers=headers)
        elif method == "DELETE":
            return await make_delete_request(url, data=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    return make_authorized_request


@pytest_asyncio.fixture
async def admin_get_request(admin_auth):
    async def inner(url, params=None):
        return await admin_auth("GET", url, params=params)

    return inner


@pytest_asyncio.fixture
async def admin_post_request(admin_auth):
    print('admin_post_request1')

    async def inner(url, data=None):
        print('admin_post_request2', url, data)
        return await admin_auth("POST", url, data=data)

    return inner


@pytest_asyncio.fixture
async def admin_put_request(admin_auth):
    async def inner(url, data=None):
        return await admin_auth("PUT", url, data=data)

    return inner


@pytest_asyncio.fixture
async def admin_delete_request(admin_auth):
    async def inner(url, data=None):
        return await admin_auth("DELETE", url, data=data)

    return inner
