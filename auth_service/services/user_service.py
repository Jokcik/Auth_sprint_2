import asyncio
import logging
from functools import lru_cache

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from opentelemetry import trace
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
        self.tracer = trace.get_tracer(f'{__name__}:{self.__class__.__name__}')

    async def login(self, user, request: Request):
        with self.tracer.start_as_current_span("login"):
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
        self.tracer = trace.get_tracer(__name__)

    def get_or_create_user_oauth(self, provider: str, user_info: dict) -> User:
        with self.tracer.start_as_current_span("get_or_create_user_oauth") as span:
            user = self.db.query(User).filter(User.oauth_provider == provider, User.oauth_id == user_info['sub']).first()
            if not user:
                user = User(
                    username=user_info.get("name", user_info.get("email")),
                    email=user_info.get("email"),
                    oauth_provider=provider,
                    oauth_id=user_info["sub"]
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            return user

    def create_user(self, user_data: UserCreate):
        with self.tracer.start_as_current_span("create_user"):
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
        with self.tracer.start_as_current_span("get_users"):
            query = self.db.query(User)
            total = query.count()
            users = query.offset((page - 1) * size).limit(size).all()
            return users, total

    def get_user_by_username(self, username: str):
        with self.tracer.start_as_current_span("get_user_by_username"):
            return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: UUID):
        with self.tracer.start_as_current_span("get_user_by_id"):
            if user := self.db.query(User).filter(User.id == user_id).first():
                return user
            raise UserNotFoundError

    def update_user(self, role_id: UUID, user_data: UserUpdate):
        with self.tracer.start_as_current_span("update_user"):
            user = self.get_user_by_id(role_id)
            if user:
                user.username = user_data.username
                user.email = user_data.email
                self.db.commit()
                self.db.refresh(user)
            return user

    def delete_role(self, role_id: UUID):
        with self.tracer.start_as_current_span("delete_role"):
            user = self.get_user_by_id(role_id)
            if user:
                self.db.delete(user)
                self.db.commit()
            return user

    def get_user_by_email(self, email: str):
        with self.tracer.start_as_current_span("get_user_by_email"):
            return self.db.query(User).filter(User.email == email).first()

    def change_password(self, user_id, password_data):
        with self.tracer.start_as_current_span("change_password"):
            user = self.get_user_by_id(user_id)
            if self.verify_password(password_data.current_password, user.hashed_password):
                user.hashed_password = self.get_password_hash(password_data.new_password)
                self.db.commit()
                self.db.refresh(user)
            else:
                raise UserWrongPasswordError

    def login_history(self, user_id, page, size):
        with self.tracer.start_as_current_span("login_history"):
            query = self.db.query(LoginHistory).filter(LoginHistory.user_id == user_id)
            total = query.count()
            histories = query.offset((page - 1) * size).limit(size).all()
            return histories, total

    def add_role_to_user(self, user_id: UUID, role_id: UUID):
        with self.tracer.start_as_current_span("add_role_to_user"):
            user = self.db.query(User).filter(User.id == user_id).first()
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if user and role:
                user.roles.append(role)
                self.db.commit()
                self.db.refresh(user)
            return user

    def remove_role_from_user(self, user_id: UUID, role_id: UUID):
        with self.tracer.start_as_current_span("remove_role_from_user"):
            user = self.get_user_by_id(user_id)
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if user and role:
                user.roles.remove(role)
                self.db.commit()
                self.db.refresh(user)
            return user

    async def register(self, user: UserCreate, request: Request = None):
        with self.tracer.start_as_current_span("register") as span:
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
                await self.login_history_service.login(db_user, request=request)
            return auth_data

    async def login(self, username: str, password: str, request: Request = None):
        with self.tracer.start_as_current_span("login") as span:
            span.set_attribute("username", username)

            with self.tracer.start_as_current_span("find_user") as span:
                db_user = self.db.query(User).filter(User.username == username).first()
                if not db_user:
                    span.set_attribute("user_found", False)
                    logging.info(f"User {username} not found")
                    raise UserNotFoundError("User not found")
                span.set_attribute("user_found", True)

            if not self.verify_password(password, db_user.hashed_password):
                span.set_attribute("password_correct", False)
                logging.info(f"Password for user {username} is incorrect")
                return None

            span.set_attribute("password_correct", True)
            auth_data = await self.auth_service.login(db_user)
            if request:
                await self.login_history_service.login(db_user, request)
            return auth_data

    def verify_password(self, plain_password, hashed_password):
        with self.tracer.start_as_current_span("verify_password") as span:
            return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        with trace.get_tracer(__name__).start_as_current_span("get_password_hash"):
            return pwd_context.hash(password)


class TokenUserService(UserService):
    # auth_service: AuthJWTService # todo ???
    # def __init__(self): # todo ???
    #     ...

    async def get_user_by_auth_credentials(self, auth_credential):
        with self.tracer.start_as_current_span("get_user_by_auth_credentials") as span:
            id = await self.auth_service.get_current_user_id(auth_credential)
            user = self.db.query(User).filter(User.id == id).first()
            if user is None:
                logging.error(f"User {id} not found")
                raise UserNotFoundError("User not found")
            return user

    async def refresh_access_token(self, refresh_token: str):  # коряво, но я не знаю, что еще
        with self.tracer.start_as_current_span("refresh_access_token") as span:
            id = await self.auth_service.refresh_access_token(refresh_token)
            user = self.db.query(User).filter(User.id == id).first()
            if user is None:
                logging.info(f"User {id} not found")
                raise UserNotFoundError("User not found")
            return self.auth_service.create_access_token(data=AuthSubSchema(sub=user.id))

    async def invalidate_token(self, token):
        with self.tracer.start_as_current_span("invalidate_token") as span:
            return self.auth_service.invalidate_token(token)


@lru_cache
def get_user_service(user_service: TokenUserService = Depends()) -> UserService:
    return user_service
