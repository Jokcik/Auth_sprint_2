import uuid

import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_get_permissions(admin_get_request, admin_post_request, permission_data):

    # Create multiple permissions
    for _ in range(15):
        data = permission_data()
        await admin_post_request("/api/v1/permissions", data)

    # Get permissions with pagination
    response, body = await admin_get_request("/api/v1/permissions?page=1&size=10")
    assert response.status == HTTPStatus.OK
    assert len(body["items"]) == 10
    assert body["total"] >= 15
    assert body["page"] == 1
    assert body["size"] == 10


async def test_create_permission(admin_post_request, permission_data):
    data = permission_data()
    response, body = await admin_post_request("/api/v1/permissions", data)
    assert response.status == HTTPStatus.OK
    assert body["name"] == data["name"]


async def test_get_permission(admin_get_request, admin_post_request, permission_data):
    data = permission_data()
    # Create permission
    response, body = await admin_post_request("/api/v1/permissions", data)
    permission_id = body["id"]

    # Get permission by ID
    response, body = await admin_get_request(f"/api/v1/permissions/{permission_id}")
    assert response.status == HTTPStatus.OK
    assert body["name"] == data["name"]


async def test_update_permission(admin_post_request, admin_put_request, permission_data):
    data = permission_data()
    # Create permission
    response, body = await admin_post_request("/api/v1/permissions", data)
    permission_id = body["id"]

    unique_id = uuid.uuid4().hex[:8]
    updated_data = {"name": f"updated_permission_{unique_id}", "description": "Updated description"}
    response, body = await admin_put_request(f"/api/v1/permissions/{permission_id}", updated_data)
    assert response.status == HTTPStatus.OK
    assert body["name"] == updated_data["name"]
    assert body["description"] == updated_data["description"]


async def test_delete_permission(admin_post_request, admin_delete_request, admin_get_request, permission_data):
    data = permission_data()
    # Create permission
    response, body = await admin_post_request("/api/v1/permissions", data)
    permission_id = body["id"]

    # Delete permission
    response, body = await admin_delete_request(f"/api/v1/permissions/{permission_id}")
    assert response.status == HTTPStatus.OK

    # Ensure permission is deleted
    response, body = await admin_get_request(f"/api/v1/permissions/{permission_id}")
    assert response.status == HTTPStatus.NOT_FOUND
