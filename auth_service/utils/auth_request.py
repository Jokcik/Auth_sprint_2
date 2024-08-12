from fastapi import Request

from models.user import User


class AuthRequest(Request):
    custom_user: User
