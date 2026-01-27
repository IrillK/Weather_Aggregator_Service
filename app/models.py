from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class WeatherService(str, Enum):
    METEOBLUE = "meteoblue"


class WeatherData(BaseModel):
    service: WeatherService
    temperature: float = Field(description="Температура в градусах Цельсия")
    feels_like: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[int] = None
    wind_speed: Optional[float] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AggregatedWeatherResponse(BaseModel):
    city: str
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    services_queried: List[WeatherService]
    average_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    data_by_service: Dict[WeatherService, WeatherData] = {}
    errors: List[str] = []
    cached: bool = False
    request_time: Optional[float] = None