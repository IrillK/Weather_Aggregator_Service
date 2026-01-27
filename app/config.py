from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # FastAPI
    app_name: str = "Weather Aggregator"
    debug: bool = False
    
    # API Keys (добавьте свои ключи в .env файл)
    meteoblue_api_key: Optional[str] = None
    
    # Настройки сервисов погоды
    weather_apis: List[str] = [
        "meteoblue", # https://my.meteoblue.com/packages/current?apikey=zeqBmpfhn4Wsb81H&lat=51.6683&lon=39.192&asl=148&format=json
    ]
    
    # Таймауты и рейт-лимиты
    request_timeout: float = 10.0
    max_requests_per_minute: int = 30
    
    # Кэширование
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600  # 60 минут в секундах
    
    class Config:
        env_file = ".env"


settings = Settings()