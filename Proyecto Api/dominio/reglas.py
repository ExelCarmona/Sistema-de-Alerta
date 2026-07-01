from typing import List, Dict, Any

from .entidades import ClimaDiario, RecomendacionPlanta
from .estrategias_recomendacion import ContextoRecomendacion, EstrategiaRecomendacion, crear_estrategias_por_defecto


class MotorRecomendacion:
    """
    Motor de reglas de negocio para recomendar cultivos domésticos
    basado en el historial de registros climáticos diarios.
    """

    def __init__(self, estrategias: List[EstrategiaRecomendacion] | None = None):
        self.estrategias = estrategias or crear_estrategias_por_defecto()

    @staticmethod
    def analizar_clima(registros_diarios: List[ClimaDiario]) -> Dict[str, Any]:
        """
        Analiza el historial diario para extraer estadísticas de temperatura y lluvia.
        """
        if not registros_diarios:
            return {
                "temperatura_promedio": 20.0,
                "temperatura_max_promedio": 25.0,
                "temperatura_min_promedio": 15.0,
                "dias_con_lluvia": 0,
                "total_lluvia": 0.0,
                "frecuencia_lluvia_pct": 0.0,
                "clasificacion_temperatura": "Templado",
                "clasificacion_lluvia": "Seco"
            }

        num_registros = len(registros_diarios)
        suma_max = 0.0
        suma_min = 0.0
        dias_con_lluvia = 0
        total_lluvia = 0.0

        for registro in registros_diarios:
            t_max = registro.temperatura_2m_max if registro.temperatura_2m_max is not None else 20.0
            t_min = registro.temperatura_2m_min if registro.temperatura_2m_min is not None else 15.0
            suma_max += t_max
            suma_min += t_min

            precip = registro.suma_precipitacion if registro.suma_precipitacion is not None else 0.0
            total_lluvia += precip
            if precip > 0.1:
                dias_con_lluvia += 1

        temp_max_promedio = suma_max / num_registros
        temp_min_promedio = suma_min / num_registros
        temp_promedio = (temp_max_promedio + temp_min_promedio) / 2
        frecuencia_lluvia_pct = (dias_con_lluvia / num_registros) * 100

        if temp_promedio < 15.0:
            clasificacion_temp = "Frío"
        elif 15.0 <= temp_promedio <= 25.0:
            clasificacion_temp = "Templado"
        else:
            clasificacion_temp = "Cálido"

        if frecuencia_lluvia_pct < 20.0:
            clasificacion_lluvia = "Seco"
        elif 20.0 <= frecuencia_lluvia_pct <= 50.0:
            clasificacion_lluvia = "Moderado"
        else:
            clasificacion_lluvia = "Húmedo"

        return {
            "temperatura_promedio": round(temp_promedio, 1),
            "temperatura_max_promedio": round(temp_max_promedio, 1),
            "temperatura_min_promedio": round(temp_min_promedio, 1),
            "dias_con_lluvia": dias_con_lluvia,
            "total_lluvia": round(total_lluvia, 1),
            "frecuencia_lluvia_pct": round(frecuencia_lluvia_pct, 1),
            "clasificacion_temperatura": clasificacion_temp,
            "clasificacion_lluvia": clasificacion_lluvia
        }

    def generar_recomendaciones(self, registros_diarios: List[ClimaDiario]) -> List[RecomendacionPlanta]:
        """
        Evalúa las reglas de negocio sobre el análisis climático y genera recomendaciones de plantas.
        """
        estadisticas = self.analizar_clima(registros_diarios)
        contexto = ContextoRecomendacion(
            temperatura_promedio=estadisticas["temperatura_promedio"],
            temperatura_max_promedio=estadisticas["temperatura_max_promedio"],
            temperatura_min_promedio=estadisticas["temperatura_min_promedio"],
            dias_con_lluvia=estadisticas["dias_con_lluvia"],
            total_lluvia=estadisticas["total_lluvia"],
            frecuencia_lluvia_pct=estadisticas["frecuencia_lluvia_pct"],
            clasificacion_temperatura=estadisticas["clasificacion_temperatura"],
            clasificacion_lluvia=estadisticas["clasificacion_lluvia"],
        )

        recomendaciones = [estrategia.recomendar(contexto) for estrategia in self.estrategias]
        orden = {"Muy Recomendado": 0, "Recomendado": 1, "No Recomendado": 2}
        recomendaciones.sort(key=lambda recomendacion: orden.get(recomendacion.nivel_recomendacion, 3))
        return recomendaciones
