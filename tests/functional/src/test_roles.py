import uuid
from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_roles(admin_get_request, admin_post_request, role_data):
    # Create multiple roles
    for _ in range(15):
        data = role_data()
        await admin_post_request("/api/v1/roles", data)

    # Get roles with pagination
    response, body = await admin_get_request("/api/v1/roles?page=1&size=10")
    assert response.status == HTTPStatus.OK
    assert len(body["items"]) == 10
    assert body["total"] >= 15
    assert body["page"] == 1
    assert body["size"] == 10


async def test_create_role(admin_post_request, role_data):
    data = role_data()
    response, body = await admin_post_request("/api/v1/roles", data)
    assert response.status == HTTPStatus.OK
    assert body["name"] == data["name"]


async def test_get_role(admin_get_request, admin_post_request, role_data):
    data = role_data()
    # Create role
    response, body = await admin_post_request("/api/v1/roles", data)
    role_id = body["id"]

    # Get role by ID
    response, body = await admin_get_request(f"/api/v1/roles/{role_id}")
    assert response.status == HTTPStatus.OK
    assert body["name"] == data["name"]


async def test_update_role(admin_post_request, admin_put_request, role_data):
    data = role_data()
    # Create role
    response, body = await admin_post_request("/api/v1/roles", data)
    role_id = body["id"]

    unique_id = uuid.uuid4().hex[:8]
    updated_data = {"name": f"updated_role_{unique_id}"}
    response, body = await admin_put_request(f"/api/v1/roles/{role_id}", updated_data)
    assert response.status == HTTPStatus.OK
    assert body["name"] == updated_data["name"]


async def test_delete_role(admin_post_request, admin_delete_request, admin_get_request, role_data):
    data = role_data()
    # Create role
    response, body = await admin_post_request("/api/v1/roles", data)
    role_id = body["id"]

    # Delete role
    response, body = await admin_delete_request(f"/api/v1/roles/{role_id}")
    assert response.status == HTTPStatus.OK

    # Ensure role is deleted
    response, body = await admin_get_request(f"/api/v1/roles/{role_id}")
    assert body == None


async def test_add_roles_to_user(user_data, admin_get_request, admin_post_request, role_data):
    data = role_data()
    response, user_info = await admin_get_request("/api/v1/auth/me")
    user_id = user_info["id"]

    # Create role
    response, body = await admin_post_request("/api/v1/roles", data)
    role_id = body["id"]

    # Add role to user
    response, body = await admin_post_request(f"/api/v1/users/{user_id}/roles", {"role_id": role_id})
    assert response.status == HTTPStatus.OK
    assert any(role["id"] == role_id for role in body["roles"])


async def test_remove_role_from_user(user_data, admin_get_request, admin_post_request, admin_delete_request, role_data):
    data = role_data()
    response, user_info = await admin_get_request("/api/v1/auth/me")
    user_id = user_info["id"]

    # Create role
    response, body = await admin_post_request("/api/v1/roles", data)
    role_id = body["id"]

    # Add role to user
    await admin_post_request(f"/api/v1/users/{user_id}/roles", {"role_id": role_id})

    # Remove role from user
    response, body = await admin_delete_request(f"/api/v1/users/{user_id}/roles/{role_id}")
    assert response.status == HTTPStatus.OK
    assert not any(role["id"] == role_id for role in body["roles"])
