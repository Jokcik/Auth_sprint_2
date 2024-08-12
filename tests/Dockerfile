# Выбираем базовый образ
FROM mirror.gcr.io/python:3.10-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /tests

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_CACHE_DIR=/var/cache/pypoetry

# Копируем файлы зависимостей
COPY ./poetry.lock ./pyproject.toml ./

# Устанавливаем зависимости
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

# Копируем тестовые файлы
COPY . /tests
