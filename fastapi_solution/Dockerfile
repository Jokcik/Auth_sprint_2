# Выбираем базовый образ
FROM mirror.gcr.io/python:3.10-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /opt/app

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

# Копируем оставшиеся файлы проекта
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем приложение FastAPI
CMD ["poetry", "run", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]

