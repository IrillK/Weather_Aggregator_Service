from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
import logging

from app.models import AggregatedWeatherResponse
from app.services.weather import weather_aggregator
from app.services.cache import cache
from app.config import settings


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/weather", response_model=AggregatedWeatherResponse)
async def get_weather(
    city: str = Query(..., min_length=2, description="Название города"),
    country_code: Optional[str] = Query(None, description="Код страны (например, 'ru', 'us')"),
    services: Optional[List[str]] = Query(
        None, 
        description="Список сервисов для опроса"
    ),
    use_cache: bool = Query(False, description="Использовать кэширование"),
    force_refresh: bool = Query(False, description="Игнорировать кэш")
) -> AggregatedWeatherResponse:
    """
    Получить агрегированные данные о погоде от нескольких сервисов.
    
    Примеры:
    - /api/v1/weather?city=Moscow&country_code=ru
    - /api/v1/weather?city=London&services=openweathermap,weatherapi
    """
    
    if services:
        # Проверяем, что все указанные сервисы поддерживаются
        invalid_services = [s for s in services if s not in settings.weather_apis]
        if invalid_services:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемые сервисы: {', '.join(invalid_services)}"
            )
    
    # Генерируем ключ для кэша
    cache_key = cache.generate_key(city, country_code, services or settings.weather_apis)
    
    # Пробуем получить из кэша
    if use_cache and not force_refresh:
        cached_data = await cache.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return AggregatedWeatherResponse(**cached_data, cached=True)
    
    # Получаем свежие данные
    try:
        result = await weather_aggregator.get_weather(
            city=city,
            country_code=country_code,
            services=services
        )
        
        # Сохраняем в кэш
        if use_cache:
            await cache.set(cache_key, result.model_dump())
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching weather for {city}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Ошибка при получении данных о погоде"
        )


@router.get("/services")
async def get_available_services():
    """Получить список доступных сервисов погоды"""
    return {
        "available_services": settings.weather_apis,
        "default_services": settings.weather_apis
    }