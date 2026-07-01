from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Localizacion:
    """
    Entidad que representa una ubicación geográfica con su información asociada de Open-Meteo.
    """
    latitud: float
    longitud: float
    elevacion: Optional[float] = None
    zona_horaria: Optional[str] = None
    utc_offset_segundos: Optional[int] = None
    id: Optional[int] = None

@dataclass
class ClimaActual:
    """
    Entidad que representa el estado del clima actual en un momento específico para una localización.
    """
    tiempo: str
    temperatura_2m: Optional[float] = None
    humedad_relativa_2m: Optional[float] = None
    codigo_clima: Optional[int] = None
    velocidad_viento_10m: Optional[float] = None
    id_localizacion: Optional[int] = None

@dataclass
class ClimaHorario:
    """
    Entidad que representa el registro o pronóstico de clima para una hora específica.
    """
    tiempo: str
    temperatura_2m: Optional[float] = None
    probabilidad_precipitacion: Optional[float] = None
    precipitacion: Optional[float] = None
    codigo_clima: Optional[int] = None
    id_localizacion: Optional[int] = None
    id: Optional[int] = None

@dataclass
class ClimaDiario:
    """
    Entidad que representa el resumen climático para un día específico.
    """
    fecha: str
    codigo_clima_max: Optional[int] = None
    temperatura_2m_max: Optional[float] = None
    temperatura_2m_min: Optional[float] = None
    suma_precipitacion: Optional[float] = None
    id_localizacion: Optional[int] = None
    id: Optional[int] = None

@dataclass
class RegistroClimatico:
    """
    Entidad compuesta que agrupa toda la información climática (actual, horaria y diaria) de una localización.
    """
    localizacion: Localizacion
    clima_actual: Optional[ClimaActual] = None
    clima_horario: List[ClimaHorario] = field(default_factory=list)
    clima_diario: List[ClimaDiario] = field(default_factory=list)

@dataclass
class RecomendacionPlanta:
    """
    Entidad que representa la sugerencia de cultivo doméstico basada en el análisis climático.
    """
    nombre: str
    nivel_recomendacion: str  # "Muy Recomendado", "Recomendado", "No Recomendado"
    dificultad: str          # "Baja", "Media", "Alta"
    justificacion: str
    consejos_cuidado: str
