from typing import Dict, Any, List
from puertos.repositorio import ClimaRepositoryPort
from dominio.entidades import RecomendacionPlanta
from dominio.reglas import MotorRecomendacion

class ObtenerRecomendacionesUseCase:
    """
    Caso de uso: Obtener Recomendaciones de Cultivos basadas en las estadísticas
    históricas/pronosticadas almacenadas para una localización determinada.
    """
    def __init__(self, repositorio: ClimaRepositoryPort):
        self.repositorio = repositorio

    def ejecutar(self, localizacion_id: int, limite_dias: int = 30) -> Dict[str, Any]:
        """
        Consulta los datos diarios de la base de datos, ejecuta el análisis
        del motor de reglas de dominio y devuelve las sugerencias junto con las estadísticas calculadas.
        """
        # 1. Obtener registros de clima diario guardados para la localización
        registros_diarios = self.repositorio.obtener_clima_diario(localizacion_id, limite=limite_dias)
        
        # 2. Si no hay datos, retornamos un resultado vacío con mensaje
        if not registros_diarios:
            return {
                "estadisticas": None,
                "recomendaciones": []
            }

        # 3. Analizar clima usando el motor de reglas en el dominio (reglas puras)
        estadisticas = MotorRecomendacion.analizar_clima(registros_diarios)
        recomendaciones = MotorRecomendacion.generar_recomendaciones(registros_diarios)

        return {
            "estadisticas": estadisticas,
            "recomendaciones": recomendaciones
        }
