from typing import Dict, Any

from aplicacion.puertos.repositorio import PuertoRepositorioClima
from dominio.reglas import MotorRecomendacion


class CasoUsoObtenerRecomendaciones:
    """
    Caso de uso: Obtener recomendaciones de cultivos basadas en las estadísticas
    históricas/pronosticadas almacenadas para una localización determinada.
    """

    def __init__(self, repositorio: PuertoRepositorioClima, motor_recomendacion: MotorRecomendacion | None = None):
        self.repositorio = repositorio
        self.motor_recomendacion = motor_recomendacion or MotorRecomendacion()

    def ejecutar(self, id_localizacion: int, limite_dias: int = 30) -> Dict[str, Any]:
        """
        Consulta los datos diarios de la base de datos, ejecuta el análisis
        del motor de reglas de dominio y devuelve las sugerencias junto con las estadísticas calculadas.
        """
        registros_diarios = self.repositorio.obtener_clima_diario(id_localizacion, limite=limite_dias)

        if not registros_diarios:
            return {
                "estadisticas": None,
                "recomendaciones": []
            }

        estadisticas = self.motor_recomendacion.analizar_clima(registros_diarios)
        recomendaciones = self.motor_recomendacion.generar_recomendaciones(registros_diarios)

        return {
            "estadisticas": estadisticas,
            "recomendaciones": recomendaciones
        }
