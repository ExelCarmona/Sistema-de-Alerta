from typing import List, Optional
from aplicacion.puertos.repositorio import PuertoRepositorioClima
from dominio.entidades import Localizacion, RegistroClimatico

class CasoUsoConsultarClima:
    """
    Caso de uso: Consultar información climática persistida en la base de datos
    para su visualización en la interfaz de usuario.
    """
    def __init__(self, repositorio: PuertoRepositorioClima):
        self.repositorio = repositorio

    def obtener_localizaciones(self) -> List[Localizacion]:
        """
        Obtiene la lista de todas las ubicaciones almacenadas en el sistema.
        """
        return self.repositorio.obtener_todas_localizaciones()

    def obtener_localizacion_por_id(self, id_localizacion: int) -> Optional[Localizacion]:
        """
        Obtiene una ubicación específica.
        """
        return self.repositorio.obtener_localizacion_por_id(id_localizacion)

    def obtener_registro_completo(self, id_localizacion: int, limite_horas: int = 168, limite_dias: int = 30) -> Optional[RegistroClimatico]:
        """
        Obtiene el reporte climático completo para una ubicación específica,
        agrupando ubicación, clima actual y pronósticos/historias guardadas.
        """
        localizacion = self.repositorio.obtener_localizacion_por_id(id_localizacion)
        if not localizacion:
            return None

        clima_actual = self.repositorio.obtener_clima_actual(id_localizacion)
        clima_horario = self.repositorio.obtener_clima_horario(id_localizacion, limite=limite_horas)
        clima_diario = self.repositorio.obtener_clima_diario(id_localizacion, limite=limite_dias)

        return RegistroClimatico(
            localizacion=localizacion,
            clima_actual=clima_actual,
            clima_horario=clima_horario,
            clima_diario=clima_diario
        )
