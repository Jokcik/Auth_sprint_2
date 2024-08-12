FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install alembic psycopg2-binary sqlalchemy

COPY alembic /app/alembic
COPY ci/env.py /app/alembic/env.py
COPY alembic.ini /app/alembic.ini
COPY ci/run_migrations.sh /app/run_migrations.sh

RUN chmod +x /app/run_migrations.sh

ENTRYPOINT ["/app/run_migrations.sh"]