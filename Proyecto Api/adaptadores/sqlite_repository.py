import sqlite3
from typing import List, Optional
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario
from aplicacion.puertos.repositorio import PuertoRepositorioClima

class RepositorioClimaSQLite(PuertoRepositorioClima):
    """
    Adaptador secundario de persistencia. Implementa PuertoRepositorioClima para interactuar
    con el archivo SQLite local (openmeteo_clima.db).
    """

    def __init__(self, ruta_bd: str):
        self.ruta_bd = ruta_bd

    def guardar_localizacion(self, localizacion: Localizacion) -> int:
        # Buscar primero si ya existe una localización cercana para evitar duplicar
        loc_existente = self.obtener_localizacion_por_coordenadas(localizacion.latitud, localizacion.longitud)
        
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
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
                conexion.commit()
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
                id_localizacion = cursor.lastrowid
                localizacion.id = id_localizacion
                conexion.commit()
                return id_localizacion
        finally:
            conexion.close()

    def obtener_localizacion_por_id(self, id_localizacion: int) -> Optional[Localizacion]:
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos 
                FROM localizaciones 
                WHERE id = ?
                """,
                (id_localizacion,)
            )
            fila = cursor.fetchone()
            if fila:
                return Localizacion(
                    id=fila[0],
                    latitud=fila[1],
                    longitud=fila[2],
                    elevacion=fila[3],
                    zona_horaria=fila[4],
                    utc_offset_segundos=fila[5]
                )
            return None
        finally:
            conexion.close()

    def obtener_localizacion_por_coordenadas(self, latitud: float, longitud: float) -> Optional[Localizacion]:
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
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
            fila = cursor.fetchone()
            if fila:
                return Localizacion(
                    id=fila[0],
                    latitud=fila[1],
                    longitud=fila[2],
                    elevacion=fila[3],
                    zona_horaria=fila[4],
                    utc_offset_segundos=fila[5]
                )
            return None
        finally:
            conexion.close()

    def obtener_todas_localizaciones(self) -> List[Localizacion]:
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                SELECT id, latitud, longitud, elevacion, zona_horaria, utc_offset_segundos 
                FROM localizaciones 
                ORDER BY id DESC
                """
            )
            filas = cursor.fetchall()
            return [
                Localizacion(
                    id=fila[0],
                    latitud=fila[1],
                    longitud=fila[2],
                    elevacion=fila[3],
                    zona_horaria=fila[4],
                    utc_offset_segundos=fila[5]
                )
                for fila in filas
            ]
        finally:
            conexion.close()

    def guardar_clima_actual(self, clima_actual: ClimaActual) -> None:
        if clima_actual.id_localizacion is None:
            raise ValueError("El clima actual debe tener un id_localizacion asignado.")
        
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO clima_actual (
                    localizacion_id, tiempo, temperatura_2m, humedad_relativa_2m, codigo_clima, velocidad_viento_10m
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    clima_actual.id_localizacion,
                    clima_actual.tiempo,
                    clima_actual.temperatura_2m,
                    clima_actual.humedad_relativa_2m,
                    clima_actual.codigo_clima,
                    clima_actual.velocidad_viento_10m
                )
            )
            conexion.commit()
        finally:
            conexion.close()

    def obtener_clima_actual(self, id_localizacion: int) -> Optional[ClimaActual]:
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                SELECT tiempo, temperatura_2m, humedad_relativa_2m, codigo_clima, velocidad_viento_10m 
                FROM clima_actual 
                WHERE localizacion_id = ?
                """,
                (id_localizacion,)
            )
            fila = cursor.fetchone()
            if fila:
                return ClimaActual(
                    tiempo=fila[0],
                    temperatura_2m=fila[1],
                    humedad_relativa_2m=fila[2],
                    codigo_clima=fila[3],
                    velocidad_viento_10m=fila[4],
                    id_localizacion=id_localizacion
                )
            return None
        finally:
            conexion.close()

    def guardar_clima_horario(self, registros_horarios: List[ClimaHorario]) -> None:
        if not registros_horarios:
            return
        
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.executemany(
                """
                INSERT OR REPLACE INTO clima_horario (
                    localizacion_id, tiempo, temperatura_2m, probabilidad_precipitacion, precipitacion, codigo_clima
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.id_localizacion,
                        r.tiempo,
                        r.temperatura_2m,
                        r.probabilidad_precipitacion,
                        r.precipitacion,
                        r.codigo_clima
                    )
                    for r in registros_horarios
                ]
            )
            conexion.commit()
        finally:
            conexion.close()

    def obtener_clima_horario(self, id_localizacion: int, limite: int = 168) -> List[ClimaHorario]:
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                SELECT id, tiempo, temperatura_2m, probabilidad_precipitacion, precipitacion, codigo_clima 
                FROM clima_horario 
                WHERE localizacion_id = ? 
                ORDER BY tiempo DESC 
                LIMIT ?
                """,
                (id_localizacion, limite)
            )
            filas = cursor.fetchall()
            # Invertimos el orden para que sea cronológico (ascendente)
            filas.reverse()
            return [
                ClimaHorario(
                    id=fila[0],
                    tiempo=fila[1],
                    temperatura_2m=fila[2],
                    probabilidad_precipitacion=fila[3],
                    precipitacion=fila[4],
                    codigo_clima=fila[5],
                    id_localizacion=id_localizacion
                )
                for fila in filas
            ]
        finally:
            conexion.close()

    def guardar_clima_diario(self, registros_diarios: List[ClimaDiario]) -> None:
        if not registros_diarios:
            return
        
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.executemany(
                """
                INSERT OR REPLACE INTO clima_diario (
                    localizacion_id, fecha, codigo_clima_max, temperatura_2m_max, temperatura_2m_min, suma_precipitacion
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        r.id_localizacion,
                        r.fecha,
                        r.codigo_clima_max,
                        r.temperatura_2m_max,
                        r.temperatura_2m_min,
                        r.suma_precipitacion
                    )
                    for r in registros_diarios
                ]
            )
            conexion.commit()
        finally:
            conexion.close()

    def obtener_clima_diario(self, id_localizacion: int, limite: int = 30) -> List[ClimaDiario]:
        conexion = sqlite3.connect(self.ruta_bd)
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """
                SELECT id, fecha, codigo_clima_max, temperatura_2m_max, temperatura_2m_min, suma_precipitacion 
                FROM clima_diario 
                WHERE localizacion_id = ? 
                ORDER BY fecha DESC 
                LIMIT ?
                """,
                (id_localizacion, limite)
            )
            filas = cursor.fetchall()
            # Invertimos el orden para que sea cronológico (ascendente)
            filas.reverse()
            return [
                ClimaDiario(
                    id=fila[0],
                    fecha=fila[1],
                    codigo_clima_max=fila[2],
                    temperatura_2m_max=fila[3],
                    temperatura_2m_min=fila[4],
                    suma_precipitacion=fila[5],
                    id_localizacion=id_localizacion
                )
                for fila in filas
            ]
        finally:
            conexion.close()
