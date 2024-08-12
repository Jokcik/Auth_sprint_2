import typer
from fastapi import FastAPI, Request, Depends
from fastapi.responses import ORJSONResponse

from api.v1 import auth, role, permission, user
from commands import cli_app
from core.config import settings
from core.lifespan import lifespan
from decorators.permissions import get_current_user_global

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"], dependencies=[Depends(get_current_user_global)])
app.include_router(role.router, prefix="/api/v1/roles", tags=["roles"], dependencies=[Depends(get_current_user_global)])
app.include_router(
    permission.router,
    prefix="/api/v1/permissions",
    tags=["permissions"],
    dependencies=[
        Depends(get_current_user_global)])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"], dependencies=[Depends(get_current_user_global)])

# Создаем новый Typer приложение для CLI команд
cli = typer.Typer()
cli.add_typer(cli_app, name="app")

if __name__ == "__main__":
    cli()
