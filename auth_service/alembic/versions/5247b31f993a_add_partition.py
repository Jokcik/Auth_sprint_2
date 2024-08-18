"""add partition

Revision ID: 5247b31f993a
Revises: 0627b0ce14fd
Create Date: 2024-08-18 17:04:16.808675

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5247b31f993a'
down_revision: Union[str, None] = '0627b0ce14fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_partition(connection, table_name, start_date, end_date):
    partition_name = f"{table_name}_{start_date.strftime('%Y_%m')}"
    connection.execute(sa.text(f"""
    CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table_name}
    FOR VALUES FROM ('{start_date}') TO ('{end_date}')
    """))
    print(f"Created partition: {partition_name}")


def upgrade():
    connection = op.get_bind()

    # Получаем текущую дату
    current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Создаем 6 партиций для следующих 6 месяцев
    for i in range(6):
        start_date = current_date
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

        create_partition(connection, 'loginhistory', start_date, end_date)

        current_date = end_date


def downgrade():
    connection = op.get_bind()

    # Получаем текущую дату
    current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Удаляем 6 партиций
    for i in range(6):
        partition_name = f"loginhistory_{current_date.strftime('%Y_%m')}"
        connection.execute(sa.text(f"DROP TABLE IF EXISTS {partition_name}"))
        print(f"Dropped partition: {partition_name}")

        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
