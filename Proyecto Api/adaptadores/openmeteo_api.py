import requests
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario, RegistroClimatico
from puertos.api_clima import ClimaApiPort

class OpenMeteoApiAdapter(ClimaApiPort):
    """
    Adaptador secundario de API externa. Implementa ClimaApiPort utilizando
    la librería requests para consumir datos climáticos de Open-Meteo.
    """

    def obtener_clima(self, latitud: float, longitud: float) -> RegistroClimatico:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitud,
            "longitude": longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error al conectar con la API de Open-Meteo: {str(e)}")

        # 1. Mapear Localización
        lat_retornada = data.get("latitude", latitud)
        lon_retornada = data.get("longitude", longitud)
        localizacion = Localizacion(
            latitud=lat_retornada,
            longitud=lon_retornada,
            elevacion=data.get("elevation"),
            zona_horaria=data.get("timezone"),
            utc_offset_segundos=data.get("utc_offset_seconds")
        )

        # 2. Mapear Clima Actual
        clima_actual = None
        current_data = data.get("current")
        if current_data:
            clima_actual = ClimaActual(
                tiempo=current_data.get("time"),
                temperatura_2m=current_data.get("temperature_2m"),
                humedad_relativa_2m=current_data.get("relative_humidity_2m"),
                codigo_clima=current_data.get("weather_code"),
                velocidad_viento_10m=current_data.get("wind_speed_10m")
            )

        # 3. Mapear Clima Horario
        clima_horario_lista = []
        hourly_data = data.get("hourly")
        if hourly_data and "time" in hourly_data:
            tiempos = hourly_data["time"]
            temps = hourly_data.get("temperature_2m", [None] * len(tiempos))
            probs = hourly_data.get("precipitation_probability", [None] * len(tiempos))
            precips = hourly_data.get("precipitation", [None] * len(tiempos))
            codigos = hourly_data.get("weather_code", [None] * len(tiempos))

            for i in range(len(tiempos)):
                clima_horario_lista.append(ClimaHorario(
                    tiempo=tiempos[i],
                    temperatura_2m=temps[i],
                    probabilidad_precipitacion=probs[i],
                    precipitacion=precips[i],
                    codigo_clima=codigos[i]
                ))

        # 4. Mapear Clima Diario
        clima_diario_lista = []
        daily_data = data.get("daily")
        if daily_data and "time" in daily_data:
            fechas = daily_data["time"]
            codigos_max = daily_data.get("weather_code", [None] * len(fechas))
            temps_max = daily_data.get("temperature_2m_max", [None] * len(fechas))
            temps_min = daily_data.get("temperature_2m_min", [None] * len(fechas))
            precip_sums = daily_data.get("precipitation_sum", [None] * len(fechas))

            for i in range(len(fechas)):
                clima_diario_lista.append(ClimaDiario(
                    fecha=fechas[i],
                    codigo_clima_max=codigos_max[i],
                    temperatura_2m_max=temps_max[i],
                    temperatura_2m_min=temps_min[i],
                    suma_precipitacion=precip_sums[i]
                ))

        return RegistroClimatico(
            localizacion=localizacion,
            clima_actual=clima_actual,
            clima_horario=clima_horario_lista,
            clima_diario=clima_diario_lista
        )
