# Проектная работа спринта
Команда:  [Максим](https://github.com/4Surpr1se) [Данил](https://github.com/Jokcik) [Александра](https://github.com/schaleksandra)

[Приглашение](https://github.com/Jokcik/Auth_sprint_2)

This is a FastAPI-based authentication service

## Setup

1. Install dependencies:
   ```
   cd auth_service
   poetry install
   ```

2. Run dependencies:
   ```
   docker-compose up redis db
   ```
   
3. Run migrations:
   ```
   docker compose up migrate
   ```

4. Run the application:
   ```
   poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Миграции базы данных

Для настройки схемы базы данных выполните следующие команды:

1. Создайте новую миграцию (если вы внесли изменения в модели):
   ```
   alembic revision --autogenerate -m "Ваше сообщение о миграции"
   ```
2. Проверить SQL-запросы, которые будут применены:
   ```
   alembic upgrade head --sql > migration.sql
   ```
3. Примените миграции:
   ```
   alembic upgrade head
   ```

## Тесты

### Локальный
Вначале нужно запустить Elasticsearch и redis:
```
docker compose -f tests/docker-compose.yml up auth_service --build
```

и запускаем тесты:
```
export PYTHONPATH=$(pwd)
poetry run pytest
```

### Docker compose
```shell
make test
```

### Flake8
```shell
pip install flake8
flake8 auth_service --max-line-length 120 --count
```

Чтобы автоматически поправить:
```shell
pip install autoflake autopep8
autoflake --in-place --remove-all-unused-imports --recursive auth_service
autopep8 --in-place --recursive --aggressive --aggressive --max-line-length 120 auth_service
```

### Задание

1. Создайте интеграцию Auth-сервиса с сервисом выдачи контента и административной панелью, используя контракт, который вы сделали в прошлом задании.
  
    При создании интеграции не забудьте учесть изящную деградацию Auth-сервиса. Auth сервис — один из самых нагруженных, потому что в него ходят большинство сервисов сайта. И если он откажет, сайт отказать не должен. Обязательно учтите этот сценарий в интеграциях с Auth-сервисом.
2. Добавьте в Auth-сервис трассировку и подключите к Jaeger. Для этого вам нужно добавить работу с заголовком x-request-id и отправку трассировок в Jaeger.
3. Добавьте в сервис механизм ограничения количества запросов к серверу.
4. Упростите регистрацию и аутентификацию пользователей в Auth-сервисе, добавив вход через социальные сервисы. Список сервисов выбирайте исходя из целевой аудитории онлайн-кинотеатра — подумайте, какими социальными сервисами они пользуются. Например, использовать [OAuth от Github](https://docs.github.com/en/free-pro-team@latest/developers/apps/authorizing-oauth-apps){target="_blank"} — не самая удачная идея. Ваши пользователи — не разработчики и вряд ли пользуются аккаунтом на Github. Лучше добавить Yandex, VK или Google.

    Вам не нужно делать фронтенд в этой задаче и реализовывать собственный сервер OAuth. Нужно реализовать протокол со стороны потребителя.
    
    Информация по OAuth у разных поставщиков данных: 
    
    - [Yandex](https://yandex.ru/dev/oauth/?turbo=true){target="_blank"},
    - [VK](https://vk.com/dev/access_token){target="_blank"},
    - [Google](https://developers.google.com/identity/protocols/oauth2){target="_blank"}.
5. Партицируйте таблицу с пользователями или с историей входов. Подумайте, по каким критериям вы бы разделили её. Важно посмотреть на таблицу не только в текущем времени, но и заглядывая в некое будущее, когда в ней будут миллионы записей. Пользователи могут быть из одной страны, но из разных регионов. А ещё пользователи могут использовать разные устройства для входа и иметь разные возрастные ограничения.
    
## Дополнительное задание
    
Реализуйте возможность открепить аккаунт в соцсети от личного кабинета. 
    
Решение залейте в репозиторий текущего спринта и отправьте на ревью.
