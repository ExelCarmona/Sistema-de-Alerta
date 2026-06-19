from typing import List, Optional
from puertos.repositorio import ClimaRepositoryPort
from dominio.entidades import Localizacion, RegistroClimatico, ClimaActual, ClimaHorario, ClimaDiario

class ConsultarClimaUseCase:
    """
    Caso de uso: Consultar información climática persistida en la base de datos
    para su visualización en la interfaz de usuario.
    """
    def __init__(self, repositorio: ClimaRepositoryPort):
        self.repositorio = repositorio

    def obtener_localizaciones(self) -> List[Localizacion]:
        """
        Obtiene la lista de todas las ubicaciones almacenadas en el sistema.
        """
        return self.repositorio.obtener_todas_localizaciones()

    def obtener_localizacion_por_id(self, localizacion_id: int) -> Optional[Localizacion]:
        """
        Obtiene una ubicación específica.
        """
        return self.repositorio.obtener_localizacion_por_id(localizacion_id)

    def obtener_registro_completo(self, localizacion_id: int, limite_horas: int = 168, limite_dias: int = 30) -> Optional[RegistroClimatico]:
        """
        Obtiene el reporte climático completo para una ubicación específica,
        agrupando ubicación, clima actual y pronósticos/historias guardadas.
        """
        localizacion = self.repositorio.obtener_localizacion_por_id(localizacion_id)
        if not localizacion:
            return None

        clima_actual = self.repositorio.obtener_clima_actual(localizacion_id)
        clima_horario = self.repositorio.obtener_clima_horario(localizacion_id, limite=limite_horas)
        clima_diario = self.repositorio.obtener_clima_diario(localizacion_id, limite=limite_dias)

        return RegistroClimatico(
            localizacion=localizacion,
            clima_actual=clima_actual,
            clima_horario=clima_horario,
            clima_diario=clima_diario
        )
