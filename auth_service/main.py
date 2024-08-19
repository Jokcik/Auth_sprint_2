import logging
import uuid

import typer
from fastapi import FastAPI, Depends, Request
from fastapi.responses import ORJSONResponse
from starlette import status

from api.v1 import auth, role, permission, user, oauth
from commands import cli_app
from core.config import settings, request_id_ctx
from core.jeager import configure_tracer
from core.lifespan import lifespan
from core.limiter import configure_limiter
from decorators.permissions import get_current_user_global

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

if settings.enable_limiters:
    configure_limiter(app)

if settings.enable_tracing:
    configure_tracer(app)


@app.middleware('http')
async def add_tracing_middleware(request: Request, call_next):
    try:
        request_id = request.headers.get('X-Request-Id') or str(uuid.uuid4())
        if not request_id:
            return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                  content={'detail': 'X-Request-Id is required'})

        request_id_ctx.set(request_id)
        response = await call_next(request)
    except Exception as e:
        logging.exception(f"Exception in middleware: {str(e)}")
        raise e

    return response


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"], dependencies=[Depends(get_current_user_global)])
app.include_router(role.router, prefix="/api/v1/roles", tags=["roles"], dependencies=[Depends(get_current_user_global)])
app.include_router(
    permission.router,
    prefix="/api/v1/permissions",
    tags=["permissions"],
    dependencies=[
        Depends(get_current_user_global)])
app.include_router(user.router, prefix="/api/v1/users", tags=["users"], dependencies=[Depends(get_current_user_global)])

app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])

# Создаем новый Typer приложение для CLI команд
cli = typer.Typer()
cli.add_typer(cli_app, name="app")

if __name__ == "__main__":
    cli()
