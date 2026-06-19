import requests
from typing import List
from app.domain.models import Location, CurrentWeather, HourlyWeather, DailyWeather, CompleteWeatherData
from app.ports.outbound.open_meteo_client import OpenMeteoClient

class HttpOpenMeteoAdapter(OpenMeteoClient):
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def fetch_weather_data(self, latitud: float, longitud: float) -> CompleteWeatherData:
        params = {
            "latitude": latitud,
            "longitude": longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse Location metadata
        location = Location(
            id=None,  # Handled by DB when saving
            latitud=data.get("latitude", latitud),
            longitud=data.get("longitude", longitud),
            elevacion=data.get("elevation"),
            zona_horaria=data.get("timezone"),
            utc_offset_segundos=data.get("utc_offset_seconds")
        )

        # Parse Current Weather
        current_data = data.get("current", {})
        current = None
        if current_data:
            current = CurrentWeather(
                localizacion_id=-1,  # Temporary, to be updated with location id
                tiempo=current_data.get("time"),
                temperatura_2m=current_data.get("temperature_2m"),
                humedad_relativa_2m=current_data.get("relative_humidity_2m"),
                codigo_clima=current_data.get("weather_code"),
                velocidad_viento_10m=current_data.get("wind_speed_10m")
            )

        # Parse Hourly Weather
        hourly_data = data.get("hourly", {})
        hourly_list: List[HourlyWeather] = []
        if hourly_data:
            times = hourly_data.get("time", [])
            temps = hourly_data.get("temperature_2m", [])
            probs = hourly_data.get("precipitation_probability", [])
            precips = hourly_data.get("precipitation", [])
            codes = hourly_data.get("weather_code", [])
            
            # Map index by index
            for i in range(len(times)):
                hourly_list.append(
                    HourlyWeather(
                        id=None,
                        localizacion_id=-1,
                        tiempo=times[i],
                        temperatura_2m=temps[i] if i < len(temps) else 0.0,
                        probabilidad_precipitacion=probs[i] if i < len(probs) else 0.0,
                        precipitacion=precips[i] if i < len(precips) else 0.0,
                        codigo_clima=codes[i] if i < len(codes) else 0
                    )
                )

        # Parse Daily Weather
        daily_data = data.get("daily", {})
        daily_list: List[DailyWeather] = []
        if daily_data:
            dates = daily_data.get("time", [])
            codes_max = daily_data.get("weather_code", [])
            temps_max = daily_data.get("temperature_2m_max", [])
            temps_min = daily_data.get("temperature_2m_min", [])
            precip_sums = daily_data.get("precipitation_sum", [])
            
            for i in range(len(dates)):
                daily_list.append(
                    DailyWeather(
                        id=None,
                        localizacion_id=-1,
                        fecha=dates[i],
                        codigo_clima_max=codes_max[i] if i < len(codes_max) else 0,
                        temperatura_2m_max=temps_max[i] if i < len(temps_max) else 0.0,
                        temperatura_2m_min=temps_min[i] if i < len(temps_min) else 0.0,
                        suma_precipitacion=precip_sums[i] if i < len(precip_sums) else 0.0
                    )
                )

        return CompleteWeatherData(
            location=location,
            current=current,
            hourly=hourly_list,
            daily=daily_list
        )
