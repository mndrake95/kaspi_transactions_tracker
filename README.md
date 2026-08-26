# 💳 Kaspi Transactions Tracker

> Личный трекер расходов из выписок Kaspi Bank

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?logo=sqlalchemy&logoColor=white)
![Tests](https://github.com/mndrake95/kaspi_transactions_tracker/actions/workflows/tests.yml/badge.svg)

---

## Что умеет

| Функция | Описание |
|---|---|
| 📤 Загрузка PDF | Парсит выписку Kaspi Bank, сохраняет транзакции |
| 🔍 Фильтрация | По месяцу и типу операции |
| 🏷️ Категории | Ручное назначение + авто-правила по ключевому слову |
| 📊 Аналитика | Графики расходов по категориям и по месяцам |

---

## Стек

- **Backend** — FastAPI + SQLAlchemy
- **База данных** — SQLite (локально) / PostgreSQL (через `DATABASE_URL`)
- **Frontend** — Bootstrap 5 + Chart.js (CDN, без сборки)

---

## Запуск

```bash
git clone https://github.com/mndrake95/kaspi_transactions_tracker.git
cd kaspi_transactions_tracker

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / Mac

pip install -r requirements.txt
cp .env.example .env
```

Запустить тесты и сервер:

```bash
pytest
uvicorn api.main:app --reload
```

Приложение будет доступно на `http://localhost:8000`.

---

## Структура проекта

```
├── api/          # FastAPI роуты
├── database/     # Модели, CRUD, сессия
├── parser/       # Парсер PDF выписок
├── services/     # Бизнес-логика (аналитика)
├── frontend/     # HTML + JS (один файл)
└── tests/        # Pytest тесты
```
