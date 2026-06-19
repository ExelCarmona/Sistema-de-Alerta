from dataclasses import dataclass
from typing import Optional, List, Dict, Any

def get_weather_description(code: int) -> Dict[str, str]:
    """
    Translates WMO weather code to description and emoji.
    """
    wmo_codes = {
        0: {"description": "Cielo Despejado", "emoji": "☀️"},
        1: {"description": "Mayormente Despejado", "emoji": "🌤️"},
        2: {"description": "Parcialmente Nublado", "emoji": "⛅"},
        3: {"description": "Cubierto / Nublado", "emoji": "☁️"},
        45: {"description": "Niebla", "emoji": "🌫️"},
        48: {"description": "Niebla Escarchada", "emoji": "🌫️"},
        51: {"description": "Llovizna Ligera", "emoji": "🌦️"},
        53: {"description": "Llovizna Moderada", "emoji": "🌦️"},
        55: {"description": "Llovizna Densa", "emoji": "🌧️"},
        56: {"description": "Llovizna Helada Ligera", "emoji": "❄️🌦️"},
        57: {"description": "Llovizna Helada Densa", "emoji": "❄️🌧️"},
        61: {"description": "Lluvia Ligera", "emoji": "🌧️"},
        63: {"description": "Lluvia Moderada", "emoji": "🌧️"},
        65: {"description": "Lluvia Fuerte", "emoji": "🌧️"},
        66: {"description": "Lluvia Helada Ligera", "emoji": "❄️🌧️"},
        67: {"description": "Lluvia Helada Fuerte", "emoji": "❄️🌧️"},
        71: {"description": "Nieve Ligera", "emoji": "❄️"},
        73: {"description": "Nieve Moderada", "emoji": "❄️"},
        75: {"description": "Nieve Fuerte", "emoji": "❄️"},
        77: {"description": "Granos de Nieve", "emoji": "❄️"},
        80: {"description": "Lluvia de Corta Duración Ligera", "emoji": "🌦️"},
        81: {"description": "Lluvia de Corta Duración Moderada", "emoji": "🌧️"},
        82: {"description": "Lluvia de Corta Duración Violenta", "emoji": "⛈️"},
        85: {"description": "Nieve de Corta Duración Ligera", "emoji": "❄️🌦️"},
        86: {"description": "Nieve de Corta Duración Fuerte", "emoji": "❄️🌧️"},
        95: {"description": "Tormenta Eléctrica", "emoji": "⛈️"},
        96: {"description": "Tormenta con Granizo Ligero", "emoji": "⛈️🌨️"},
        99: {"description": "Tormenta con Granizo Fuerte", "emoji": "⛈️🌨️"},
    }
    return wmo_codes.get(code, {"description": "Desconocido", "emoji": "❓"})

@dataclass
class Location:
    id: Optional[int]
    latitud: float
    longitud: float
    elevacion: Optional[float]
    zona_horaria: Optional[str]
    utc_offset_segundos: Optional[int]

@dataclass
class CurrentWeather:
    localizacion_id: int
    tiempo: str
    temperatura_2m: float
    humedad_relativa_2m: float
    codigo_clima: int
    velocidad_viento_10m: float

    @property
    def clima_info(self) -> Dict[str, str]:
        return get_weather_description(self.codigo_clima)

@dataclass
class HourlyWeather:
    id: Optional[int]
    localizacion_id: int
    tiempo: str
    temperatura_2m: float
    probabilidad_precipitacion: float
    precipitacion: float
    codigo_clima: int

    @property
    def clima_info(self) -> Dict[str, str]:
        return get_weather_description(self.codigo_clima)

@dataclass
class DailyWeather:
    id: Optional[int]
    localizacion_id: int
    fecha: str
    codigo_clima_max: int
    temperatura_2m_max: float
    temperatura_2m_min: float
    suma_precipitacion: float

    @property
    def clima_info(self) -> Dict[str, str]:
        return get_weather_description(self.codigo_clima_max)

@dataclass
class CompleteWeatherData:
    location: Location
    current: Optional[CurrentWeather]
    hourly: List[HourlyWeather]
    daily: List[DailyWeather]
