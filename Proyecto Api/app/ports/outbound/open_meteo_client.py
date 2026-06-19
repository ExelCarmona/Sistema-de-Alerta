from abc import ABC, abstractmethod
from app.domain.models import CompleteWeatherData

class OpenMeteoClient(ABC):
    @abstractmethod
    def fetch_weather_data(self, latitud: float, longitud: float) -> CompleteWeatherData:
        """
        Fetches current, hourly, and daily weather data from the Open-Meteo API.
        """
        pass
