import typer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from models.user import User
from models.role import Role
from core.roles import UserRole
from passlib.context import CryptContext

cli_app = typer.Typer()

pwd_context = CryptContext(schemes=["bcrypt"])


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@cli_app.command()
def create_admin(
        username: str = typer.Option("admin"),
        email: str = typer.Option("admin@example.com"),
        password: str = typer.Option("adminpassword")
):
    session = SessionLocal()
    try:
        # Проверяем, существует ли уже администратор с таким именем пользователя
        existing_admin = session.query(User).filter(User.username == username).first()
        if existing_admin:
            typer.echo(f"Администратор с именем пользователя {username} уже существует. Ничего не делаем.")
            return

        # Проверяем, существует ли уже роль админа
        admin_role = session.query(Role).filter(Role.name == UserRole.ADMIN.value).first()
        if not admin_role:
            admin_role = Role(name=UserRole.ADMIN.value, description="Администратор системы")
            session.add(admin_role)

        # Создаем пользователя-админа
        hashed_password = get_password_hash(password)
        admin_user = User(username=username, email=email, hashed_password=hashed_password)
        admin_user.roles.append(admin_role)

        session.add(admin_user)
        session.commit()

        typer.echo(f"Администратор {username} успешно создан")
    except Exception as e:
        session.rollback()
        typer.echo(f"Ошибка при создании администратора: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    cli_app()
