import sqlite3
from typing import List, Optional
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario
from puertos.repositorio import ClimaRepositoryPort

class SQLiteClimaRepository(ClimaRepositoryPort):
    """
    Adaptador secundario de persistencia. Implementa ClimaRepositoryPort para interactuar
    con el archivo SQLite local (openmeteo_clima.db).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def guardar_localizacion(self, localizacion: Localizacion) -> int:
        # Buscar primero si ya existe una localización cercana para evitar duplicar
        loc_existente = self.obtener_localizacion_por_coordenadas(localizacion.latitud, localizacion.longitud)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if loc_existente:
                # Actualizar los valores en caso de que existan datos nuevos
                cursor.execute(
                    """
                    UPDATE localizaciones 
                    SET elevacion = ?, zona_horaria = ?, utc_offset_segundos = ? 
                    WHERE id = ?
                    """,
                    (localizacion.elevacion, localizacion.zona_horaria, localizacion.utc_offset_segundos, loc_existente.id)
                )
                localizacion.id = loc_existente.id
                conn.commit()
                return loc_existente.id
            else:
                # Insertar nuevo registro
                cursor.execute(
                    """
                    INSERT INTO localizaciones (latitud, longitud, elevacion, zona_horaria, utc_offset_segundos) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (localizacion.latitud, localizacion.longitud, localizacion.elevacion, localizacion.zona_horaria, localizacion.utc_offset_segundos)
                )
                localizacion_id = cursor.lastrowid
                localizacion.id = localizacion_id
                conn.commit()
                return localizacion_id
        finally:
            conn.close()

    def obtener_localizacion_por_id(self, localizacion_id: int) -> Optional[Localizacion]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos 
                FROM localizaciones 
                WHERE id = ?
                """,
                (localizacion_id,)
            )
            row = cursor.fetchone()
            if row:
                return Localizacion(
                    id=row[0],
                    latitud=row[1],
                    longitud=row[2],
                    elevacion=row[3],
                    zona_horaria=row[4],
                    utc_offset_segundos=row[5]
                )
            return None
        finally:
            conn.close()

    def obtener_localizacion_por_coordenadas(self, latitud: float, longitud: float) -> Optional[Localizacion]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Para evitar problemas de precisión flotante en SQLite, comparamos con un delta pequeño (0.01 grados)
            # Esto también nos permite reutilizar localizaciones si el usuario busca una coordenada muy similar.
            cursor.execute(
                """
                SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos 
                FROM localizaciones 
                WHERE ABS(latitud - ?) < 0.01 AND ABS(longitud - ?) < 0.01 
                LIMIT 1
                """,
                (latitud, longitud)
            )
            row = cursor.fetchone()
            if row:
                return Localizacion(
                    id=row[0],
                    latitud=row[1],
                    longitud=row[2],
                    elevacion=row[3],
                    zona_horaria=row[4],
                    utc_offset_segundos=row[5]
                )
            return None
        finally:
            conn.close()

    def obtener_todas_localizaciones(self) -> List[Localizacion]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos 
                FROM localizaciones 
                ORDER BY id DESC
                """
            )
            rows = cursor.fetchall()
            return [
                Localizacion(
                    id=row[0],
                    latitud=row[1],
                    longitud=row[2],
                    elevacion=row[3],
                    zona_horaria=row[4],
                    utc_offset_segundos=row[5]
                )
                for row in rows
            ]
        finally:
            conn.close()

    def guardar_clima_actual(self, clima_actual: ClimaActual) -> None:
        if clima_actual.localizacion_id is None:
            raise ValueError("El clima actual debe tener un localizacion_id asignado.")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO clima_actual (
                    localizacion_id, tiempo, temperatura_2m, humedad_relativa_2m, codigo_clima, velocidad_viento_10m
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    clima_actual.localizacion_id,
                    clima_actual.tiempo,
                    clima_actual.temperatura_2m,
                    clima_actual.humedad_relativa_2m,
                    clima_actual.codigo_clima,
                    clima_actual.velocidad_viento_10m
                )
            )
            conn.commit()
        finally:
            conn.close()

    def obtener_clima_actual(self, localizacion_id: int) -> Optional[ClimaActual]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT tiempo, temperatura_2m, humedad_relativa_2m, codigo_clima, velocidad_viento_10m 
                FROM clima_actual 
                WHERE localizacion_id = ?
                """,
                (localizacion_id,)
            )
            row = cursor.fetchone()
            if row:
                return ClimaActual(
                    tiempo=row[0],
                    temperatura_2m=row[1],
                    humedad_relativa_2m=row[2],
                    codigo_clima=row[3],
                    velocidad_viento_10m=row[4],
                    localizacion_id=localizacion_id
                )
            return None
        finally:
            conn.close()

    def guardar_clima_horario(self, registros_horarios: List[ClimaHorario]) -> None:
        if not registros_horarios:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.executemany(
                """
                INSERT OR REPLACE INTO clima_horario (
                    localizacion_id, tiempo, temperatura_2m, probabilidad_precipitacion, precipitacion, codigo_clima
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.localizacion_id,
                        r.tiempo,
                        r.temperatura_2m,
                        r.probabilidad_precipitacion,
                        r.precipitacion,
                        r.codigo_clima
                    )
                    for r in registros_horarios
                ]
            )
            conn.commit()
        finally:
            conn.close()

    def obtener_clima_horario(self, localizacion_id: int, limite: int = 168) -> List[ClimaHorario]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, tiempo, temperatura_2m, probabilidad_precipitacion, precipitacion, codigo_clima 
                FROM clima_horario 
                WHERE localizacion_id = ? 
                ORDER BY tiempo DESC 
                LIMIT ?
                """,
                (localizacion_id, limite)
            )
            rows = cursor.fetchall()
            # Invertimos el orden para que sea cronológico (ascendente)
            rows.reverse()
            return [
                ClimaHorario(
                    id=row[0],
                    tiempo=row[1],
                    temperatura_2m=row[2],
                    probabilidad_precipitacion=row[3],
                    precipitacion=row[4],
                    codigo_clima=row[5],
                    localizacion_id=localizacion_id
                )
                for row in rows
            ]
        finally:
            conn.close()

    def guardar_clima_diario(self, registros_diarios: List[ClimaDiario]) -> None:
        if not registros_diarios:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.executemany(
                """
                INSERT OR REPLACE INTO clima_diario (
                    localizacion_id, fecha, codigo_clima_max, temperatura_2m_max, temperatura_2m_min, suma_precipitacion
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.localizacion_id,
                        r.fecha,
                        r.codigo_clima_max,
                        r.temperatura_2m_max,
                        r.temperatura_2m_min,
                        r.suma_precipitacion
                    )
                    for r in registros_diarios
                ]
            )
            conn.commit()
        finally:
            conn.close()

    def obtener_clima_diario(self, localizacion_id: int, limite: int = 30) -> List[ClimaDiario]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, fecha, codigo_clima_max, temperatura_2m_max, temperatura_2m_min, suma_precipitacion 
                FROM clima_diario 
                WHERE localizacion_id = ? 
                ORDER BY fecha DESC 
                LIMIT ?
                """,
                (localizacion_id, limite)
            )
            rows = cursor.fetchall()
            # Invertimos el orden para que sea cronológico (ascendente)
            rows.reverse()
            return [
                ClimaDiario(
                    id=row[0],
                    fecha=row[1],
                    codigo_clima_max=row[2],
                    temperatura_2m_max=row[3],
                    temperatura_2m_min=row[4],
                    suma_precipitacion=row[5],
                    localizacion_id=localizacion_id
                )
                for row in rows
            ]
        finally:
            conn.close()
