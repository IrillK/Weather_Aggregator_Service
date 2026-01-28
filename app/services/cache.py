import json
from typing import Optional, Any
#import aioredis
from redis import asyncio as aioredis
from app.config import settings


class RedisCache:
    """Асинхронный кэш на Redis"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Установить соединение с Redis"""
        self.redis = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Закрыть соединение с Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить данные из кэша"""
        if not self.redis:
            await self.connect()
        
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Сохранить данные в кэш"""
        if not self.redis:
            await self.connect()
        
        ttl = ttl or settings.cache_ttl
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    
    def generate_key(self, city: str, country_code: Optional[str], services: list) -> str:
        """Сгенерировать ключ для кэша"""
        services_str = "_".join(sorted(services))
        country_str = country_code or "any"
        return f"weather:{city}:{country_str}:{services_str}"


# Глобальный экземпляр кэша
cache = RedisCache()