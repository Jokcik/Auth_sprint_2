FROM mirror.gcr.io/python:3.10-slim-bookworm

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV GUNICORN_PROCESSES 1
ENV GUNICORN_THREADS 16
ENV GUNICORN_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'
ENV POETRY_CACHE_DIR=/var/cache/pypoetry

COPY poetry.lock pyproject.toml ./

RUN  pip install poetry \
     && poetry --no-root install --no-dev

COPY entrypoint.sh run_gunicorn.sh
COPY gunicorn.conf.py gunicorn.conf.py


COPY . .

EXPOSE 8000

ENTRYPOINT ["/opt/app/entrypoint.sh"]
