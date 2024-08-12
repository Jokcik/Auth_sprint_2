import logging
from functools import lru_cache

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.roles import UserRole
from services.auth_service import AuthSubSchema, get_auth_service, AuthJWTService
from db.database import get_db
from models.user import User, LoginHistory
from models.role import Role
from uuid import UUID
from psycopg2 import errors

from services.role_service import RoleService
from schemas.user import UserUpdate, UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

UniqueViolation = errors.lookup('23505')


class UserNotFoundError(Exception):
    pass


class UserWrongPasswordError(Exception):
    pass


class UserUniqueError(Exception):
    pass


class LoginHistoryService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def login(self, user, request: Request):
        log = LoginHistory(user_id=user.id,
                           ip_address=request.client.host,
                           user_agent=request.headers.get('User-Agent')
                           )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log


class UserService:
    def __init__(self, db: Session = Depends(get_db),
                 auth_service: AuthJWTService = Depends(get_auth_service),
                 role_service: RoleService = Depends(),
                 login_history_service: LoginHistoryService = Depends()):
        self.db = db
        self.auth_service = auth_service
        self.role_service = role_service
        self.login_history_service = login_history_service

    def create_user(self, user_data: UserCreate):
        user = User(username=user_data.username, email=user_data.email,
                    hashed_password=self.get_password_hash(user_data.password))
        self.db.add(user)
        try:
            self.db.commit()
        except UniqueViolation as e:
            raise UserUniqueError(e.pgerror)
        self.db.refresh(user)
        return user

    def get_users(self, page, size):
        query = self.db.query(User)
        total = query.count()
        users = query.offset((page - 1) * size).limit(size).all()
        return users, total

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: UUID):
        if user := self.db.query(User).filter(User.id == user_id).first():
            return user
        raise UserNotFoundError

    def update_user(self, role_id: UUID, user_data: UserUpdate):
        user = self.get_user_by_id(role_id)
        if user:
            user.username = user_data.username
            user.email = user_data.email
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_role(self, role_id: UUID):
        user = self.get_user_by_id(role_id)
        if user:
            self.db.delete(user)
            self.db.commit()
        return user

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def change_password(self, user_id, password_data):
        user = self.get_user_by_id(user_id)
        if self.verify_password(password_data.current_password, user.hashed_password):
            user.hashed_password = self.get_password_hash(password_data.new_password)
            self.db.commit()
            self.db.refresh(user)
        else:
            raise UserWrongPasswordError

    def login_history(self, user_id, page, size):
        query = self.db.query(LoginHistory).filter(LoginHistory.user_id == user_id)
        total = query.count()
        histories = query.offset((page - 1) * size).limit(size).all()
        return histories, total

    def add_role_to_user(self, user_id: UUID, role_id: UUID):
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if user and role:
            user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        return user

    def remove_role_from_user(self, user_id: UUID, role_id: UUID):
        user = self.get_user_by_id(user_id)
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if user and role:
            user.roles.remove(role)
            self.db.commit()
            self.db.refresh(user)
        return user

    async def register(self, user: UserCreate, request: Request = None):
        # todo это же два запроса, которая бд потом сама сделает, нет?
        if self.db.query(User).filter(User.username == user.username).first():
            raise ValueError("Username already registered")
        if self.db.query(User).filter(User.email == user.email).first():
            raise ValueError("Email already registered")
        db_user = User(username=user.username, email=user.email, hashed_password=self.get_password_hash(user.password))
        # Добавляем пользователю роль по умолчанию, например, "user"
        default_role = self.role_service.get_role_by_name(UserRole.USER)
        if default_role:
            db_user.roles.append(default_role)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        auth_data = await self.auth_service.register(db_user)
        if request:
            self.login_history_service.login(db_user, request=request)
        return auth_data

    async def login(self, username: str, password: str, request: Request = None):
        db_user = self.db.query(User).filter(User.username == username).first()
        if not db_user:
            logging.info(f"User {username} not found")
            raise UserNotFoundError("User not found")
        if not self.verify_password(password, db_user.hashed_password):
            logging.info(f"Password for user {username} is incorrect")
            return None
        auth_data = await self.auth_service.login(db_user)
        if request:
            self.login_history_service.login(db_user, request)
        return auth_data

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


class TokenUserService(UserService):
    # auth_service: AuthJWTService # todo ???
    # def __init__(self): # todo ???
    #     ...

    async def get_user_by_auth_credentials(self, auth_credential):
        id = await self.auth_service.get_current_user_id(auth_credential)
        user = self.db.query(User).filter(User.id == id).first()
        if user is None:
            logging.error(f"User {id} not found")
            raise UserNotFoundError("User not found")
        return user

    async def refresh_access_token(self, refresh_token: str):  # коряво, но я не знаю, что еще
        id = await self.auth_service.refresh_access_token(refresh_token)
        user = self.db.query(User).filter(User.id == id).first()
        if user is None:
            logging.info(f"User {id} not found")
            raise UserNotFoundError("User not found")
        return self.auth_service.create_access_token(data=AuthSubSchema(sub=user.id))

    async def invalidate_token(self, token):
        return self.auth_service.invalidate_token(token)


@lru_cache
def get_user_service(user_service: TokenUserService = Depends()) -> UserService:
    return user_service
