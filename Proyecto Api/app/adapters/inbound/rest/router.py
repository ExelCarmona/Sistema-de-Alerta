from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from app.ports.inbound.weather_use_cases import WeatherUseCases

router = APIRouter(prefix="/api")

# Pydantic Schemas
class LocationCreateRequest(BaseModel):
    latitud: float = Field(..., description="Latitude of the location", ge=-90.0, le=90.0)
    longitud: float = Field(..., description="Longitude of the location", ge=-180.0, le=180.0)

class LocationResponse(BaseModel):
    id: int
    latitud: float
    longitud: float
    elevacion: Optional[float] = None
    zona_horaria: Optional[str] = None
    utc_offset_segundos: Optional[int] = None

    class Config:
        from_attributes = True

class WeatherDescription(BaseModel):
    description: str
    emoji: str

class CurrentWeatherResponse(BaseModel):
    tiempo: str
    temperatura_2m: float
    humedad_relativa_2m: float
    codigo_clima: int
    velocidad_viento_10m: float
    clima_info: WeatherDescription

class HourlyWeatherResponse(BaseModel):
    tiempo: str
    temperatura_2m: float
    probabilidad_precipitacion: float
    precipitacion: float
    codigo_clima: int
    clima_info: WeatherDescription

class DailyWeatherResponse(BaseModel):
    fecha: str
    codigo_clima_max: int
    temperatura_2m_max: float
    temperatura_2m_min: float
    suma_precipitacion: float
    clima_info: WeatherDescription

class WeatherResponse(BaseModel):
    location: LocationResponse
    current: Optional[CurrentWeatherResponse] = None
    hourly: List[HourlyWeatherResponse]
    daily: List[DailyWeatherResponse]

# Dependency to get weather use cases from app state
def get_weather_service(request: Request) -> WeatherUseCases:
    return request.app.state.weather_service

@router.get("/locations", response_model=List[LocationResponse])
def list_locations(service: WeatherUseCases = Depends(get_weather_service)):
    """
    List all registered locations in the system.
    """
    try:
        return service.list_locations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/locations", response_model=LocationResponse, status_code=201)
def add_location(payload: LocationCreateRequest, service: WeatherUseCases = Depends(get_weather_service)):
    """
    Register a new location and fetch its initial weather data.
    """
    try:
        return service.add_location(payload.latitud, payload.longitud)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/locations/{location_id}/weather", response_model=WeatherResponse)
def get_weather(location_id: int, service: WeatherUseCases = Depends(get_weather_service)):
    """
    Get full weather details (current, hourly, daily) for a location.
    """
    weather_data = service.get_weather(location_id)
    if not weather_data:
        raise HTTPException(status_code=404, detail=f"Location with ID {location_id} not found.")
    return weather_data

@router.post("/locations/{location_id}/sync", response_model=WeatherResponse)
def sync_weather(location_id: int, service: WeatherUseCases = Depends(get_weather_service)):
    """
    Force-sync weather data from Open-Meteo for a specific location.
    """
    try:
        return service.sync_weather(location_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
