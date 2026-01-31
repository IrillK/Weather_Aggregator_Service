from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.api.v1.endpoints import weather
from app.services.weather import weather_aggregator
from app.services.cache import cache
from app.config import settings


# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("Starting up Weather Aggregator Service...")
    # Подключаем кэш
    await cache.connect()
    logger.info("Cache connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await weather_aggregator.close()
    await cache.disconnect()
    logger.info("Service stopped")


# Создаем FastAPI приложение
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Подключаем роутеры
app.include_router(
    weather.router,
    prefix="/api/v1",
    tags=["weather"]
)


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья сервиса"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "cache_connected": cache.redis is not None
    }


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Weather Aggregator Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "weather": "/api/v1/weather",
            "services": "/api/v1/services",
            "health": "/health"
        }
    }