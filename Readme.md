weather_service/
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа FastAPI
│   ├── config.py         # Конфигурация
│   ├── dependencies.py   # Зависимости
│   ├── models.py         # Pydantic модели
│   ├── services/
│   │   ├── __init__.py
│   │   ├── weather.py    # Логика получения погоды
│   │   └── cache.py      # Кэширование
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── endpoints/
│               ├── __init__.py
│               └── weather.py # Эндпоинты
├── requirements.txt
└── .env.example
