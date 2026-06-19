from typing import List, Optional
from app.domain.models import Location, CompleteWeatherData
from app.ports.inbound.weather_use_cases import WeatherUseCases
from app.ports.outbound.weather_repository import WeatherRepository
from app.ports.outbound.open_meteo_client import OpenMeteoClient

class WeatherService(WeatherUseCases):
    def __init__(self, repository: WeatherRepository, open_meteo_client: OpenMeteoClient):
        self.repository = repository
        self.open_meteo_client = open_meteo_client

    def get_weather(self, location_id: int) -> Optional[CompleteWeatherData]:
        # 1. Fetch location from DB
        location = self.repository.get_location_by_id(location_id)
        if not location:
            return None
        
        # 2. Fetch current weather from DB
        current = self.repository.get_current_weather(location_id)
        
        # 3. Fetch hourly weather from DB
        hourly = self.repository.get_hourly_weather(location_id)
        
        # 4. Fetch daily weather from DB
        daily = self.repository.get_daily_weather(location_id)
        
        # If database weather tables are empty, fetch from API and save
        if not current or not hourly or not daily:
            try:
                return self.sync_weather(location_id)
            except Exception as e:
                # If sync fails (e.g., rate limit or network issue), return what we have
                pass
        
        return CompleteWeatherData(
            location=location,
            current=current,
            hourly=hourly,
            daily=daily
        )

    def list_locations(self) -> List[Location]:
        return self.repository.list_locations()

    def add_location(self, latitud: float, longitud: float) -> Location:
        # Check if location already exists (by approximate coordinates)
        existing = self.repository.find_location_by_coords(latitud, longitud)
        if existing:
            return existing
        
        # Fetch metadata and weather from API
        weather_data = self.open_meteo_client.fetch_weather_data(latitud, longitud)
        
        # Save location (gets ID populated)
        new_location = self.repository.save_location(weather_data.location)
        
        # Save associated weather data
        if weather_data.current:
            weather_data.current.localizacion_id = new_location.id
            self.repository.save_current_weather(weather_data.current)
            
        if weather_data.hourly:
            self.repository.save_hourly_weather(new_location.id, weather_data.hourly)
            
        if weather_data.daily:
            self.repository.save_daily_weather(new_location.id, weather_data.daily)
            
        return new_location

    def sync_weather(self, location_id: int) -> CompleteWeatherData:
        location = self.repository.get_location_by_id(location_id)
        if not location:
            raise ValueError(f"Ubicación con ID {location_id} no encontrada.")
            
        # Fetch fresh data from API
        weather_data = self.open_meteo_client.fetch_weather_data(location.latitud, location.longitud)
        
        # Keep local ID
        weather_data.location.id = location_id
        self.repository.save_location(weather_data.location)
        
        # Save fresh weather data
        if weather_data.current:
            weather_data.current.localizacion_id = location_id
            self.repository.save_current_weather(weather_data.current)
            
        if weather_data.hourly:
            self.repository.save_hourly_weather(location_id, weather_data.hourly)
            
        if weather_data.daily:
            self.repository.save_daily_weather(location_id, weather_data.daily)
            
        return CompleteWeatherData(
            location=weather_data.location,
            current=weather_data.current,
            hourly=weather_data.hourly,
            daily=weather_data.daily
        )
