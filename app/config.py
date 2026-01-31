from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # FastAPI
    app_name: str = "Weather Aggregator"
    debug: bool = False
    
    # API Keys (ключи в .env файле)
    meteoblue_api_key: Optional[str] = None
    
    # Настройки сервисов погоды
    weather_apis: List[str] = [
        "meteoblue", 
    ]
    
    # Таймауты и рейт-лимиты
    request_timeout: float = 10.0
    max_requests_per_minute: int = 30
    
    # Кэширование
    redis_url: str = "redis://redis:6379"  # docker_compouse Или проброс сети
    #redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600  # 60 минут в секундах


settings = Settings()