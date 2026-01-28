from geopy.geocoders import Photon

from typing import Optional, Tuple

def geocode(city: str) -> Optional[Tuple]:
    """Функция для определения координат по адресу"""
    # Вынести функцию в отдельный пакет сервисы
    geolocator = Photon(user_agent="geoapiExercises")  
    location = geolocator.geocode(city)

    return (location.latitude, location.longitude)
