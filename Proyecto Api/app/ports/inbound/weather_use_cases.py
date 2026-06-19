from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Location, CompleteWeatherData

class WeatherUseCases(ABC):
    @abstractmethod
    def get_weather(self, location_id: int) -> Optional[CompleteWeatherData]:
        """
        Gets current, hourly and daily weather data for a given location.
        """
        pass

    @abstractmethod
    def list_locations(self) -> List[Location]:
        """
        Lists all registered locations in the system.
        """
        pass

    @abstractmethod
    def add_location(self, latitud: float, longitud: float) -> Location:
        """
        Registers a new location, retrieves metadata (timezone, elevation) 
        and initial weather data from Open-Meteo, and saves it.
        """
        pass

    @abstractmethod
    def sync_weather(self, location_id: int) -> CompleteWeatherData:
        """
        Forces synchronization of weather data from Open-Meteo 
        for a registered location, updating the local database.
        """
        pass
