import sqlite3
from typing import List, Optional
from app.domain.models import Location, CurrentWeather, HourlyWeather, DailyWeather
from app.ports.outbound.weather_repository import WeatherRepository

class SQLiteWeatherRepository(WeatherRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """
        Creates tables if they don't exist to ensure database setup is self-healing.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table localizaciones
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS localizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitud REAL NOT NULL,
                longitud REAL NOT NULL,
                elevacion REAL,
                zona_horaria TEXT,
                utc_offset_segundos INTEGER
            );
            """)

            # Table clima_actual
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clima_actual (
                localizacion_id INTEGER PRIMARY KEY,
                tiempo TEXT NOT NULL,
                temperatura_2m REAL NOT NULL,
                humedad_relativa_2m REAL NOT NULL,
                codigo_clima INTEGER NOT NULL,
                velocidad_viento_10m REAL NOT NULL,
                FOREIGN KEY (localizacion_id) REFERENCES localizaciones(id) ON DELETE CASCADE
            );
            """)

            # Table clima_horario
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clima_horario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                localizacion_id INTEGER NOT NULL,
                tiempo TEXT NOT NULL,
                temperatura_2m REAL NOT NULL,
                probabilidad_precipitacion REAL NOT NULL,
                precipitacion REAL NOT NULL,
                codigo_clima INTEGER NOT NULL,
                FOREIGN KEY (localizacion_id) REFERENCES localizaciones(id) ON DELETE CASCADE
            );
            """)

            # Table clima_diario
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clima_diario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                localizacion_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                codigo_clima_max INTEGER NOT NULL,
                temperatura_2m_max REAL NOT NULL,
                temperatura_2m_min REAL NOT NULL,
                suma_precipitacion REAL NOT NULL,
                FOREIGN KEY (localizacion_id) REFERENCES localizaciones(id) ON DELETE CASCADE
            );
            """)
            conn.commit()

    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos FROM localizaciones WHERE id = ?",
                (location_id,)
            )
            row = cursor.fetchone()
            if row:
                return Location(
                    id=row["id"],
                    latitud=row["latitud"],
                    longitud=row["longitud"],
                    elevacion=row["elevacion"],
                    zona_horaria=row["zona_horaria"],
                    utc_offset_segundos=row["utc_offset_segundos"]
                )
            return None

    def find_location_by_coords(self, latitud: float, longitud: float) -> Optional[Location]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Tolerance for matching coords (e.g. 0.01 degree)
            cursor.execute(
                "SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos "
                "FROM localizaciones "
                "WHERE abs(latitud - ?) < 0.01 AND abs(longitud - ?) < 0.01",
                (latitud, longitud)
            )
            row = cursor.fetchone()
            if row:
                return Location(
                    id=row["id"],
                    latitud=row["latitud"],
                    longitud=row["longitud"],
                    elevacion=row["elevacion"],
                    zona_horaria=row["zona_horaria"],
                    utc_offset_segundos=row["utc_offset_segundos"]
                )
            return None

    def list_locations(self) -> List[Location]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos FROM localizaciones")
            rows = cursor.fetchall()
            return [
                Location(
                    id=row["id"],
                    latitud=row["latitud"],
                    longitud=row["longitud"],
                    elevacion=row["elevacion"],
                    zona_horaria=row["zona_horaria"],
                    utc_offset_segundos=row["utc_offset_segundos"]
                )
                for row in rows
            ]

    def save_location(self, location: Location) -> Location:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if location.id:
                cursor.execute(
                    "UPDATE localizaciones SET latitud = ?, longitud = ?, elevacion = ?, zona_horaria = ?, utc_offset_segundos = ? WHERE id = ?",
                    (location.latitud, location.longitud, location.elevacion, location.zona_horaria, location.utc_offset_segundos, location.id)
                )
                conn.commit()
                return location
            else:
                cursor.execute(
                    "INSERT INTO localizaciones (latitud, longitud, elevacion, zona_horaria, utc_offset_segundos) VALUES (?, ?, ?, ?, ?)",
                    (location.latitud, location.longitud, location.elevacion, location.zona_horaria, location.utc_offset_segundos)
                )
                location.id = cursor.lastrowid
                conn.commit()
                return location

    def get_current_weather(self, location_id: int) -> Optional[CurrentWeather]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT localizacion_id, tiempo, temperatura_2m, humedad_relativa_2m, codigo_clima, velocidad_viento_10m "
                "FROM clima_actual WHERE localizacion_id = ?",
                (location_id,)
            )
            row = cursor.fetchone()
            if row:
                return CurrentWeather(
                    localizacion_id=row["localizacion_id"],
                    tiempo=row["tiempo"],
                    temperatura_2m=row["temperatura_2m"],
                    humedad_relativa_2m=row["humedad_relativa_2m"],
                    codigo_clima=row["codigo_clima"],
                    velocidad_viento_10m=row["velocidad_viento_10m"]
                )
            return None

    def save_current_weather(self, current: CurrentWeather) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO clima_actual (localizacion_id, tiempo, temperatura_2m, humedad_relativa_2m, codigo_clima, velocidad_viento_10m) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (current.localizacion_id, current.tiempo, current.temperatura_2m, current.humedad_relativa_2m, current.codigo_clima, current.velocidad_viento_10m)
            )
            conn.commit()

    def get_hourly_weather(self, location_id: int) -> List[HourlyWeather]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, localizacion_id, tiempo, temperatura_2m, probabilidad_precipitacion, precipitacion, codigo_clima "
                "FROM clima_horario WHERE localizacion_id = ? ORDER BY tiempo ASC",
                (location_id,)
            )
            rows = cursor.fetchall()
            return [
                HourlyWeather(
                    id=row["id"],
                    localizacion_id=row["localizacion_id"],
                    tiempo=row["tiempo"],
                    temperatura_2m=row["temperatura_2m"],
                    probabilidad_precipitacion=row["probabilidad_precipitacion"],
                    precipitacion=row["precipitacion"],
                    codigo_clima=row["codigo_clima"]
                )
                for row in rows
            ]

    def save_hourly_weather(self, location_id: int, hourly_list: List[HourlyWeather]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Clear previous entries to prevent duplicate timestamps for the location
            cursor.execute("DELETE FROM clima_horario WHERE localizacion_id = ?", (location_id,))
            
            for hourly in hourly_list:
                cursor.execute(
                    "INSERT INTO clima_horario (localizacion_id, tiempo, temperatura_2m, probabilidad_precipitacion, precipitacion, codigo_clima) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (location_id, hourly.tiempo, hourly.temperatura_2m, hourly.probabilidad_precipitacion, hourly.precipitacion, hourly.codigo_clima)
                )
            conn.commit()

    def get_daily_weather(self, location_id: int) -> List[DailyWeather]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, localizacion_id, fecha, codigo_clima_max, temperatura_2m_max, temperatura_2m_min, suma_precipitacion "
                "FROM clima_diario WHERE localizacion_id = ? ORDER BY fecha ASC",
                (location_id,)
            )
            rows = cursor.fetchall()
            return [
                DailyWeather(
                    id=row["id"],
                    localizacion_id=row["localizacion_id"],
                    fecha=row["fecha"],
                    codigo_clima_max=row["codigo_clima_max"],
                    temperatura_2m_max=row["temperatura_2m_max"],
                    temperatura_2m_min=row["temperatura_2m_min"],
                    suma_precipitacion=row["suma_precipitacion"]
                )
                for row in rows
            ]

    def save_daily_weather(self, location_id: int, daily_list: List[DailyWeather]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Clear previous entries
            cursor.execute("DELETE FROM clima_diario WHERE localizacion_id = ?", (location_id,))
            
            for daily in daily_list:
                cursor.execute(
                    "INSERT INTO clima_diario (localizacion_id, fecha, codigo_clima_max, temperatura_2m_max, temperatura_2m_min, suma_precipitacion) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (location_id, daily.fecha, daily.codigo_clima_max, daily.temperatura_2m_max, daily.temperatura_2m_min, daily.suma_precipitacion)
                )
            conn.commit()
