from abc import ABC, abstractmethod
from typing import List, Optional
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario

class PuertoRepositorioClima(ABC):
    """
    Puerto de repositorio abstracto. Define la interfaz para el almacenamiento
    y recuperación de datos climáticos (persistencia).
    """

    @abstractmethod
    def guardar_localizacion(self, localizacion: Localizacion) -> int:
        """
        Guarda o actualiza una localización en el almacén de datos.
        Retorna el ID autogenerado o existente de la localización.
        """
        pass

    @abstractmethod
    def obtener_localizacion_por_id(self, id_localizacion: int) -> Optional[Localizacion]:
        """
        Obtiene una localización por su ID.
        """
        pass

    @abstractmethod
    def obtener_localizacion_por_coordenadas(self, latitud: float, longitud: float) -> Optional[Localizacion]:
        """
        Obtiene una localización basada en sus coordenadas geográficas exactas (o muy cercanas).
        """
        pass

    @abstractmethod
    def obtener_todas_localizaciones(self) -> List[Localizacion]:
        """
        Obtiene una lista con todas las localizaciones registradas.
        """
        pass

    @abstractmethod
    def guardar_clima_actual(self, clima_actual: ClimaActual) -> None:
        """
        Guarda o actualiza el clima actual asociado a una localización.
        """
        pass

    @abstractmethod
    def obtener_clima_actual(self, id_localizacion: int) -> Optional[ClimaActual]:
        """
        Obtiene el clima actual guardado para una localización específica.
        """
        pass

    @abstractmethod
    def guardar_clima_horario(self, registros_horarios: List[ClimaHorario]) -> None:
        """
        Guarda una lista de registros de clima horario.
        Debe sobreescribir registros existentes en caso de conflicto por (id_localizacion, tiempo).
        """
        pass

    @abstractmethod
    def obtener_clima_horario(self, id_localizacion: int, limite: int = 168) -> List[ClimaHorario]:
        """
        Obtiene el historial de clima horario de una localización, ordenado por tiempo.
        El límite por defecto es 168 (1 semana).
        """
        pass

    @abstractmethod
    def guardar_clima_diario(self, registros_diarios: List[ClimaDiario]) -> None:
        """
        Guarda una lista de registros de clima diario.
        Debe sobreescribir registros existentes en caso de conflicto por (id_localizacion, fecha).
        """
        pass

    @abstractmethod
    def obtener_clima_diario(self, id_localizacion: int, limite: int = 30) -> List[ClimaDiario]:
        """
        Obtiene el historial de clima diario de una localización, ordenado por fecha.
        El límite por defecto es 30 (1 mes).
        """
        pass
