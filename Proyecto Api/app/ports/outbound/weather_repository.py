from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import Location, CurrentWeather, HourlyWeather, DailyWeather

class WeatherRepository(ABC):
    @abstractmethod
    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        """
        Retrieves a location by its unique ID.
        """
        pass

    @abstractmethod
    def find_location_by_coords(self, latitud: float, longitud: float) -> Optional[Location]:
        """
        Finds a location by latitude and longitude.
        """
        pass

    @abstractmethod
    def list_locations(self) -> List[Location]:
        """
        Lists all locations.
        """
        pass

    @abstractmethod
    def save_location(self, location: Location) -> Location:
        """
        Saves a location to the database. Returns the location with its ID populated.
        """
        pass

    @abstractmethod
    def get_current_weather(self, location_id: int) -> Optional[CurrentWeather]:
        """
        Gets the current weather for a location.
        """
        pass

    @abstractmethod
    def save_current_weather(self, current: CurrentWeather) -> None:
        """
        Saves or updates the current weather for a location.
        """
        pass

    @abstractmethod
    def get_hourly_weather(self, location_id: int) -> List[HourlyWeather]:
        """
        Gets hourly weather records for a location.
        """
        pass

    @abstractmethod
    def save_hourly_weather(self, location_id: int, hourly_list: List[HourlyWeather]) -> None:
        """
        Saves a list of hourly weather records, replacing any existing records for the same hours.
        """
        pass

    @abstractmethod
    def get_daily_weather(self, location_id: int) -> List[DailyWeather]:
        """
        Gets daily weather records for a location.
        """
        pass

    @abstractmethod
    def save_daily_weather(self, location_id: int, daily_list: List[DailyWeather]) -> None:
        """
        Saves a list of daily weather records, replacing any existing records for the same days.
        """
        pass
