from abc import ABC, abstractmethod
from dominio.entidades import RegistroClimatico

class PuertoApiClima(ABC):
    """
    Puerto de API climática abstracta. Define la interfaz para conectarse con
    servicios climáticos externos (como Open-Meteo).
    """

    @abstractmethod
    def obtener_clima(self, latitud: float, longitud: float) -> RegistroClimatico:
        """
        Consulta un servicio climático externo para obtener el pronóstico o historial
        climático (actual, horario y diario) de las coordenadas indicadas.
        Retorna un objeto de dominio RegistroClimatico estructurado.
        """
        pass
