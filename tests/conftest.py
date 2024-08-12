import asyncio
import pytest


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


pytest_plugins = [
    'tests.functional.fixtures.postgres_fixture',
    'tests.functional.fixtures.api_fixture',
    'tests.functional.fixtures.redis_fixture',
]

import pytest
import uuid
from faker import Faker


@pytest.fixture
def user_data():
    fake = Faker()
    unique_id = uuid.uuid4().hex[:8]  # Используем первые 8 символов UUID

    username = f"user_{unique_id}"
    email = f"{username}@{fake.domain_name()}"
    password = f"pass_{uuid.uuid4().hex[:12]}"  # Используем первые 12 символов UUID для пароля

    user_data = {
        "username": username,
        "email": email,
        "password": password
    }

    return user_data

@pytest.fixture
def role_data():
    def _generate_role_data():
        fake = Faker()
        unique_id = uuid.uuid4().hex[:8]  # Используем первые 8 символов UUID

        return {
            "name": fake.word() + "_role_" + unique_id,
            "description": "Test role description"
        }

    return _generate_role_data


@pytest.fixture
def permission_data():
    def _generate_permission_data():
        fake = Faker()
        unique_id = uuid.uuid4().hex[:8]  # Используем первые 8 символов UUID

        return {
            "name": fake.word() + "_permission_" + unique_id,
            "description": "Test permission description"
        }

    return _generate_permission_data
