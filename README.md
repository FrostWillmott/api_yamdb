# Описание проекта

Проект **YaMDb** собирает отзывы пользователей на различные произведения. Пользователи могут оставлять отзывы, ставить оценки и комментировать отзывы других пользователей. Проект поддерживает различные категории и жанры произведений.

## Стек технологий

- Python
- Django
- Django REST Framework
- PostgreSQL

## Раздел с авторами

- Автор 1: Иван Ткаченко [https://github.com/FrostWillmott](https://github.com/FrostWillmott)
- Автор 2: Николай Волосянков [https://github.com/intrening](https://github.com/intrening)
- Автор 3: Олег Ларионов [https://github.com/Oleg202020](https://github.com/Oleg202020)

## Как открыть документацию?

Документация API доступна по адресу `/api/v1/redoc/` после запуска сервера. Она предоставляет подробное описание всех доступных эндпоинтов и их параметров.

## Пример запросов/ответов

### Пример запроса на регистрацию пользователя

**POST** `/api/v1/auth/signup/`

Пример запроса:

```json
{
  "email": "user@example.com",
  "username": "^w\\Z"
}
```

Пример ответа:

```json
{
  "email": "string",
  "username": "string"
}
```

## Как запустить проект

### Клонирование репозитория

Склонируйте репозиторий на локальную машину:

```bash
git clone https://github.com/FrostWillmott/api_yamdb
```

### Установка зависимостей

Перейдите в директорию проекта и установите зависимости с помощью pip:

```bash
pip install -r requirements.txt
```

### Настройка базы данных

Создайте базу данных и примените миграции:

```bash
python manage.py migrate
```

### Запуск сервера

Запустите сервер разработки Django:

```bash
python manage.py runserver
```

Теперь проект доступен по адресу `http://127.0.0.1:8000/`.

### Тестирование

Для запуска тестов используйте команду:

```bash
pytest
```

Как загрузить данные из csv файла в базу данных:

Выполните команду в sql консоли:

```bash
LOAD DATA INFILE '/home/export_file.csv' INTO TABLE table_name FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '/n' IGNORE 1 ROWS;
```