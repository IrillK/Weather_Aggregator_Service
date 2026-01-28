import asyncio
import httpx
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from asyncio_throttle import Throttler

from app.config import settings
from app.models import WeatherData, WeatherService, AggregatedWeatherResponse

logger = logging.getLogger(__name__)

class WeatherServiceClient:
    """Базовый класс для клиентов погодных сервисов"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        self.throttler = Throttler(rate_limit=settings.max_requests_per_minute, period=60)
        
    async def close(self):
        await self.client.aclose()
    
    async def fetch_weather(self, city: str, country_code: Optional[str] = None) -> Optional[WeatherData]:
        """Абстрактный метод, должен быть реализован в дочерних классах"""
        raise NotImplementedError

class MeteoblueenClient(WeatherServiceClient):
    """Клиент для meteoblue API"""
    
    BASE_URL = "https://my.meteoblue.com/packages/current"
    
    async def fetch_weather(self, city: str) -> Optional[WeatherData]:
        async with self.throttler:
            try:
                lat, lon = geocode(city)
                params = {
                    "lat": lat,
                    "lon": lon,
                    "apikey": settings.meteoblue_api_key,
                    "asl": "148"
                }
                
                response = await self.client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                return WeatherData(
                    service=WeatherService.METEOBLUE,
                    temperature=data["data_current"]["temperature"],
                    #feels_like=data["main"]["feels_like"],
                    #humidity=data["main"]["humidity"],
                    #pressure=data["main"]["pressure"],
                    #wind_speed=data["wind"]["speed"],
                    #description=data["weather"][0]["description"],
                    #icon=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}.png"
                )
                
            except Exception as e:
                logger.error(f"OpenWeather API error for {city}: {str(e)}")
                return None

class OpenWeatherClient(WeatherServiceClient):
    """Клиент для OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    async def fetch_weather(self, city: str, country_code: Optional[str] = None) -> Optional[WeatherData]:
        async with self.throttler:
            try:
                params = {
                    "q": f"{city},{country_code}" if country_code else city,
                    "appid": settings.openweather_api_key,
                    "units": "metric",
                    "lang": "ru"
                }
                
                response = await self.client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                return WeatherData(
                    service=WeatherService.OPENWEATHER,
                    temperature=data["main"]["temp"],
                    feels_like=data["main"]["feels_like"],
                    humidity=data["main"]["humidity"],
                    pressure=data["main"]["pressure"],
                    wind_speed=data["wind"]["speed"],
                    description=data["weather"][0]["description"],
                    icon=f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}.png"
                )
                
            except Exception as e:
                logger.error(f"OpenWeather API error for {city}: {str(e)}")
                return None

class WeatherAggregator:
    """Основной сервис для агрегации данных от разных провайдеров"""
    
    def __init__(self):
        self.clients = {
            WeatherService.METEOBLUE: MeteoblueenClient(),
            # Добавьте другие клиенты по аналогии
        }
    
    async def get_weather(
        self, 
        city: str, # Сделать перекодирование города в координаты
        country_code: Optional[str] = None,
        services: Optional[List[str]] = None
    ) -> AggregatedWeatherResponse:
        """Получить погоду от нескольких сервисов одновременно"""
        
        if services is None:
            services = settings.weather_apis
        
        start_time = datetime.now()
        
        # Создаем задачи для всех выбранных сервисов
        tasks = []
        for service_name in services:
            if service_name in self.clients:
                task = self.clients[service_name].fetch_weather(city, country_code)
                tasks.append(task)
        
        # Запускаем все задачи конкурентно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обрабатываем результаты
        weather_data = {}
        errors = []
        temperatures = []
        
        for service_name, result in zip(services, results):
            if isinstance(result, Exception):
                errors.append(f"{service_name}: {str(result)}")
            elif result:
                weather_data[service_name] = result
                temperatures.append(result.temperature)
        
        # Вычисляем агрегированные показатели
        avg_temp = sum(temperatures) / len(temperatures) if temperatures else None
        
        response = AggregatedWeatherResponse(
            city=city,
            country=country_code,
            services_queried=[WeatherService(s) for s in services],
            average_temperature=avg_temp,
            min_temperature=min(temperatures) if temperatures else None,
            max_temperature=max(temperatures) if temperatures else None,
            data_by_service=weather_data,
            errors=errors,
            request_time=(datetime.now() - start_time).total_seconds()
        )
        
        return response
    
    async def close(self):
        """Корректно закрываем все клиенты"""
        for client in self.clients.values():
            await client.close()


# Создаем глобальный экземпляр агрегатора
weather_aggregator = WeatherAggregator()