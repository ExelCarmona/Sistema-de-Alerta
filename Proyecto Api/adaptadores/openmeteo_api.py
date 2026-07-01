import requests
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario, RegistroClimatico
from aplicacion.puertos.api_clima import PuertoApiClima

class AdaptadorApiOpenMeteo(PuertoApiClima):
    """
    Adaptador secundario de API externa. Implementa PuertoApiClima utilizando
    la librería requests para consumir datos climáticos de Open-Meteo.
    """

    def obtener_clima(self, latitud: float, longitud: float) -> RegistroClimatico:
        url = "https://api.open-meteo.com/v1/forecast"
        parametros = {
            "latitude": latitud,
            "longitude": longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,precipitation_probability,precipitation,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }

        try:
            respuesta = requests.get(url, params=parametros, timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error al conectar con la API de Open-Meteo: {str(e)}")

        # 1. Mapear Localización
        lat_retornada = datos.get("latitude", latitud)
        lon_retornada = datos.get("longitude", longitud)
        localizacion = Localizacion(
            latitud=lat_retornada,
            longitud=lon_retornada,
            elevacion=datos.get("elevation"),
            zona_horaria=datos.get("timezone"),
            utc_offset_segundos=datos.get("utc_offset_seconds")
        )

        # 2. Mapear Clima Actual
        clima_actual = None
        datos_actuales = datos.get("current")
        if datos_actuales:
            clima_actual = ClimaActual(
                tiempo=datos_actuales.get("time"),
                temperatura_2m=datos_actuales.get("temperature_2m"),
                humedad_relativa_2m=datos_actuales.get("relative_humidity_2m"),
                codigo_clima=datos_actuales.get("weather_code"),
                velocidad_viento_10m=datos_actuales.get("wind_speed_10m")
            )

        # 3. Mapear Clima Horario
        clima_horario_lista = []
        datos_horarios = datos.get("hourly")
        if datos_horarios and "time" in datos_horarios:
            tiempos = datos_horarios["time"]
            temperaturas = datos_horarios.get("temperature_2m", [None] * len(tiempos))
            probabilidades = datos_horarios.get("precipitation_probability", [None] * len(tiempos))
            precipitaciones = datos_horarios.get("precipitation", [None] * len(tiempos))
            codigos = datos_horarios.get("weather_code", [None] * len(tiempos))

            for i in range(len(tiempos)):
                clima_horario_lista.append(ClimaHorario(
                    tiempo=tiempos[i],
                    temperatura_2m=temperaturas[i],
                    probabilidad_precipitacion=probabilidades[i],
                    precipitacion=precipitaciones[i],
                    codigo_clima=codigos[i]
                ))

        # 4. Mapear Clima Diario
        clima_diario_lista = []
        datos_diarios = datos.get("daily")
        if datos_diarios and "time" in datos_diarios:
            fechas = datos_diarios["time"]
            codigos_max = datos_diarios.get("weather_code", [None] * len(fechas))
            temperaturas_max = datos_diarios.get("temperature_2m_max", [None] * len(fechas))
            temperaturas_min = datos_diarios.get("temperature_2m_min", [None] * len(fechas))
            sumas_precipitacion = datos_diarios.get("precipitation_sum", [None] * len(fechas))

            for i in range(len(fechas)):
                clima_diario_lista.append(ClimaDiario(
                    fecha=fechas[i],
                    codigo_clima_max=codigos_max[i],
                    temperatura_2m_max=temperaturas_max[i],
                    temperatura_2m_min=temperaturas_min[i],
                    suma_precipitacion=sumas_precipitacion[i]
                ))

        return RegistroClimatico(
            localizacion=localizacion,
            clima_actual=clima_actual,
            clima_horario=clima_horario_lista,
            clima_diario=clima_diario_lista
        )
