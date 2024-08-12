"""Add default roles

Revision ID: 0627b0ce14fd
Revises: b38e16cca450
Create Date: 2024-08-10 12:48:35.907416

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String
from uuid import uuid4

# revision identifiers, used by Alembic.
revision: str = '0627b0ce14fd'
down_revision: Union[str, None] = 'b38e16cca450'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем временную таблицу roles для вставки данных
    roles_table = table('roles',
                        column('id', String),
                        column('name', String),
                        column('description', String)
                        )

    # Вставляем роли ADMIN и USER
    op.bulk_insert(roles_table,
                   [
                       {'id': str(uuid4()), 'name': 'ADMIN', 'description': 'Администратор системы'},
                       {'id': str(uuid4()), 'name': 'USER', 'description': 'Обычный пользователь'}
                   ]
                   )


def downgrade() -> None:
    # Удаляем вставленные роли
    op.execute("DELETE FROM roles WHERE name IN ('ADMIN', 'USER')")
