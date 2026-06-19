from typing import List, Dict, Any
from .entidades import ClimaDiario, RecomendacionPlanta

class MotorRecomendacion:
    """
    Motor de reglas de negocio para recomendar cultivos domésticos
    basado en el historial de registros climáticos diarios.
    """

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

        for r in registros_diarios:
            t_max = r.temperatura_2m_max if r.temperatura_2m_max is not None else 20.0
            t_min = r.temperatura_2m_min if r.temperatura_2m_min is not None else 15.0
            suma_max += t_max
            suma_min += t_min
            
            precip = r.suma_precipitacion if r.suma_precipitacion is not None else 0.0
            total_lluvia += precip
            if precip > 0.1:  # Se considera día lluvioso si cae más de 0.1 mm
                dias_con_lluvia += 1

        temp_max_promedio = suma_max / num_registros
        temp_min_promedio = suma_min / num_registros
        temp_promedio = (temp_max_promedio + temp_min_promedio) / 2
        frecuencia_lluvia_pct = (dias_con_lluvia / num_registros) * 100

        # Clasificar temperatura
        if temp_promedio < 15.0:
            clasificacion_temp = "Frío"
        elif 15.0 <= temp_promedio <= 25.0:
            clasificacion_temp = "Templado"
        else:
            clasificacion_temp = "Cálido"

        # Clasificar lluvia
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

    @classmethod
    def generar_recomendaciones(cls, registros_diarios: List[ClimaDiario]) -> List[RecomendacionPlanta]:
        """
        Evalúa las reglas de negocio sobre el análisis climático y genera recomendaciones de plantas.
        """
        stats = cls.analizar_clima(registros_diarios)
        t_prom = stats["temperatura_promedio"]
        t_min = stats["temperatura_min_promedio"]
        t_max = stats["temperatura_max_promedio"]
        frec_lluvia = stats["frecuencia_lluvia_pct"]

        recomendaciones = []

        # 1. Tomate
        # Prefiere temperaturas templadas a cálidas
        if 18.0 <= t_prom <= 28.0 and t_min >= 10.0:
            nivel = "Muy Recomendado"
            just = f"La temperatura promedio de {t_prom}°C y mínimas estables ({t_min}°C) son óptimas para la floración y maduración del tomate."
            if frec_lluvia < 25.0:
                just += " Al ser una zona de bajas lluvias, se previenen enfermedades fúngicas, pero necesitará riego manual constante en el suelo."
            else:
                just += " Las lluvias de la zona aportarán humedad, pero vigile que el suelo drene bien para evitar hongos."
        elif 12.0 <= t_prom < 18.0:
            nivel = "Recomendado"
            just = f"Aunque el clima es algo fresco (promedio {t_prom}°C), el tomate puede crecer si se siembra en un lugar con sol directo o protegida de vientos fríos."
        else:
            nivel = "No Recomendado"
            just = f"La temperatura promedio ({t_prom}°C) está fuera del rango ideal para el tomate. En climas muy fríos no prosperará y en muy cálidos las flores se caen."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Tomate",
            nivel_recomendacion=nivel,
            dificultad="Media",
            justificacion=just,
            consejos_cuidado="Requiere al menos 6 horas de sol directo. Riegue la base sin mojar las hojas para evitar plagas y coloque un tutor (soporte) a medida que crezca."
        ))

        # 2. Albahaca
        # Sensible al frío extremo, le encanta el calor moderado y el agua
        if 16.0 <= t_prom <= 27.0 and t_min >= 12.0:
            nivel = "Muy Recomendado"
            just = f"Clima cálido/templado ideal para la albahaca (promedio {t_prom}°C). Estimula el crecimiento de hojas aromáticas tiernas."
        elif 10.0 <= t_prom < 16.0:
            nivel = "Recomendado"
            just = f"El clima templado-frío ({t_prom}°C) ralentiza su crecimiento. Se aconseja cultivarla en macetas para poder resguardarla dentro de casa si bajan las temperaturas."
        else:
            nivel = "No Recomendado"
            just = f"Las bajas temperaturas (mínima promedio de {t_min}°C) o el calor extremo marchitarán rápidamente la albahaca al aire libre."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Albahaca",
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=just,
            consejos_cuidado="Prefiere riego frecuente manteniendo la tierra húmeda pero sin encharcar. Pellizque las puntas y retire las flores para promover más hojas."
        ))

        # 3. Lechuga
        # Prefiere clima fresco
        if 10.0 <= t_prom <= 20.0:
            nivel = "Muy Recomendado"
            just = f"El rango de temperatura templado-frío ({t_prom}°C) es perfecto para la lechuga, evitando que se espigue (florezca prematuramente y se ponga amarga)."
        elif 20.0 < t_prom <= 25.0:
            nivel = "Recomendado"
            just = f"Temperatura templada ({t_prom}°C). Se puede cultivar pero requiere sombra parcial durante las horas más cálidas del día para evitar que se deshidrate."
        else:
            nivel = "No Recomendado"
            just = f"La temperatura promedio ({t_prom}°C) es inadecuada. Si es muy fría se hiela y si es muy cálida espigará casi de inmediato."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Lechuga",
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=just,
            consejos_cuidado="Riego ligero pero frecuente para mantener la humedad superficial. Use suelos ricos en materia orgánica y coseche las hojas exteriores gradualmente."
        ))

        # 4. Espinaca
        # Prefiere clima frío
        if 8.0 <= t_prom <= 17.0:
            nivel = "Muy Recomendado"
            just = f"Clima fresco ideal ({t_prom}°C). La espinaca soporta heladas ligeras y produce hojas tiernas y dulces en estas condiciones."
        elif 17.0 < t_prom <= 22.0:
            nivel = "Recomendado"
            just = f"Temperatura de {t_prom}°C. Es posible cultivarla bajo la sombra de plantas más altas y manteniendo el suelo húmedo."
        else:
            nivel = "No Recomendado"
            just = f"La temperatura promedio ({t_prom}°C) es demasiado alta. La espinaca entrará en floración muy rápido y sus hojas se volverán duras y amargas."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Espinaca",
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=just,
            consejos_cuidado="Siembre en semisombra en climas intermedios. Mantenga el suelo fresco y húmedo mediante acolchado (mulch) orgánico."
        ))

        # 5. Romero y Tomillo (Hierbas Mediterráneas)
        # Prefieren sol, calor y suelo seco
        if t_prom >= 14.0 and frec_lluvia <= 35.0:
            nivel = "Muy Recomendado"
            just = f"Clima templado/cálido ({t_prom}°C) y con lluvias moderadas a secas ({frec_lluvia}%). Recrea las condiciones mediterráneas ideales para el romero y tomillo."
        elif t_prom >= 12.0:
            nivel = "Recomendado"
            just = f"El romero tolerará el clima, pero debido a la frecuencia de lluvias del {frec_lluvia}%, se debe asegurar un sustrato muy poroso y con excelente drenaje en maceta."
        else:
            nivel = "No Recomendado"
            just = f"El clima frío promedio ({t_prom}°C) y la alta humedad pueden pudrir las raíces del romero al aire libre. Intente cultivar en interiores bien iluminados."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Romero y Tomillo",
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=just,
            consejos_cuidado="Riegue solo cuando la tierra esté completamente seca. Son plantas perennes que requieren mínimo mantenimiento una vez establecidas."
        ))

        # 6. Menta
        # Muy adaptable pero requiere humedad
        if frec_lluvia >= 30.0 or t_prom <= 22.0:
            nivel = "Muy Recomendado"
            just = f"La menta adora la humedad o el clima fresco/templado (promedio {t_prom}°C). Su crecimiento será vigoroso."
        else:
            nivel = "Recomendado"
            just = f"Es una planta muy resistente que crecerá en clima seco ({frec_lluvia}% de lluvias), siempre y cuando el usuario se comprometa a regarla abundantemente."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Menta",
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=just,
            consejos_cuidado="Se recomienda cultivarla en macetas individuales debido a su naturaleza invasiva. Tolera bien la semisombra y necesita riego frecuente."
        ))

        # 7. Zanahoria
        # Prefiere clima fresco a templado
        if 12.0 <= t_prom <= 22.0:
            nivel = "Muy Recomendado"
            just = f"El rango de {t_prom}°C es óptimo para el desarrollo uniforme de la raíz de la zanahoria."
        elif 8.0 <= t_prom < 12.0 or 22.0 < t_prom <= 26.0:
            nivel = "Recomendado"
            just = f"Las temperaturas promedio ({t_prom}°C) son viables, aunque en climas más cálidos las raíces pueden volverse fibrosas o cortas."
        else:
            nivel = "No Recomendado"
            just = f"Las temperaturas extremas ({t_prom}°C promedio) dificultan la germinación y desarrollo de las raíces."

        recomendaciones.append(RecomendacionPlanta(
            nombre="Zanahoria",
            nivel_recomendacion=nivel,
            dificultad="Media",
            justificacion=just,
            consejos_cuidado="Requiere un suelo muy suelto y libre de piedras para que la raíz crezca recta. Mantenga una humedad constante durante la germinación."
        ))

        # Ordenar las recomendaciones: Primero "Muy Recomendado", luego "Recomendado", luego "No Recomendado"
        orden = {"Muy Recomendado": 0, "Recomendado": 1, "No Recomendado": 2}
        recomendaciones.sort(key=lambda x: orden.get(x.nivel_recomendacion, 3))

        return recomendaciones
