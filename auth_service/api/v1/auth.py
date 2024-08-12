import logging

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordBearer

from schemas.user import UserCreate, User as UserSchema, Token, UserLogin
from services.auth_service import TokenValidationError
from services.user_service import UserNotFoundError, TokenUserService
from services.user_service import UserService, get_user_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=Token,
             summary="Регистрация нового пользователя",
             description="Создает нового пользователя в системе и возвращает токены доступа и обновления.")
async def register(user: UserCreate,
                   request: Request,
                   user_service: UserService = Depends(get_user_service)):
    logging.debug(f"Registering user: {user.username}")
    try:
        return await user_service.register(user, request=request)
    except ValueError as e:
        logging.info(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token,
             summary="Вход пользователя в систему",
             description="Аутентифицирует пользователя и возвращает токены доступа и обновления.")
async def login(user_data: UserLogin,
                request: Request,
                user_service: UserService = Depends(get_user_service)
                ):
    try:
        result = await user_service.login(user_data.username, user_data.password, request=request)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


@router.post("/logout",
             summary="Выход пользователя из системы",
             description="Инвалидирует текущий токен доступа пользователя.")
async def logout(token: str = Depends(oauth2_scheme),
                 user_service: TokenUserService = Depends(get_user_service)):
    await user_service.invalidate_token(token)
    return {"detail": "Successfully logged out"}


@router.post("/refresh", response_model=Token,
             summary="Обновление токена доступа",
             description="Создает новый токен доступа на основе действительного токена обновления.")
async def refresh_token(
        refresh_token: str = Body(..., embed=True),
        user_service: TokenUserService = Depends(get_user_service),
):
    try:
        new_access_token = await user_service.refresh_access_token(refresh_token)
    except (TokenValidationError, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": new_access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema,
            summary="Получение информации о текущем пользователе",
            description="Возвращает данные аутентифицированного пользователя.")
async def read_users_me(
        user_service: TokenUserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
):
    user = await user_service.get_user_by_auth_credentials(token)
    return user
