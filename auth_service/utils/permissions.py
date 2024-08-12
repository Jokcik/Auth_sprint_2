from typing import List
from models.user import User


def has_permission(user: User, permission_name: str) -> bool:
    for role in user.roles:
        for permission in role.permissions:
            if permission.name == permission_name:
                return True
    return False


def has_role(user: User, role_name: str) -> bool:
    return any(role.name == role_name for role in user.roles)


def get_user_permissions(user: User) -> List[str]:
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return list(permissions)
