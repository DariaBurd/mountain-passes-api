# mountain-passes-api

API для добавления и модерации горных перевалов

## Установка
1. Установите зависимости: `pip install -r requirements.txt`
2. Настройте базу данных: `python init_db.py`
3. Запустите сервер: `uvicorn app:app --reload`

## Эндпоинты
- POST /submitData - добавить перевал
- GET /submitData/{id} - получить перевал по ID
- PATCH /submitData/{id} - редактировать перевал
- GET /submitData/?user__email=... - перевалы пользователя

## Документация
Swagger docs: http://localhost:8000/docs
