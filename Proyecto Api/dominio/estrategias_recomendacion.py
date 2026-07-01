from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from .entidades import RecomendacionPlanta


@dataclass(frozen=True)
class ContextoRecomendacion:
    """Valores agregados que alimentan las estrategias de recomendación."""

    temperatura_promedio: float
    temperatura_max_promedio: float
    temperatura_min_promedio: float
    dias_con_lluvia: int
    total_lluvia: float
    frecuencia_lluvia_pct: float
    clasificacion_temperatura: str
    clasificacion_lluvia: str


class EstrategiaRecomendacion(ABC):
    """Contrato mínimo para una regla de recomendación de cultivo."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        raise NotImplementedError


class EstrategiaTomate(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Tomate"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio
        t_min = contexto.temperatura_min_promedio
        frec_lluvia = contexto.frecuencia_lluvia_pct

        if 18.0 <= t_prom <= 28.0 and t_min >= 10.0:
            nivel = "Muy Recomendado"
            justificacion = (
                f"La temperatura promedio de {t_prom}°C y mínimas estables ({t_min}°C) son óptimas para la floración y maduración del tomate."
            )
            if frec_lluvia < 25.0:
                justificacion += " Al ser una zona de bajas lluvias, se previenen enfermedades fúngicas, pero necesitará riego manual constante en el suelo."
            else:
                justificacion += " Las lluvias de la zona aportarán humedad, pero vigile que el suelo drene bien para evitar hongos."
        elif 12.0 <= t_prom < 18.0:
            nivel = "Recomendado"
            justificacion = f"Aunque el clima es algo fresco (promedio {t_prom}°C), el tomate puede crecer si se siembra en un lugar con sol directo o protegida de vientos fríos."
        else:
            nivel = "No Recomendado"
            justificacion = f"La temperatura promedio ({t_prom}°C) está fuera del rango ideal para el tomate. En climas muy fríos no prosperará y en muy cálidos las flores se caen."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Media",
            justificacion=justificacion,
            consejos_cuidado="Requiere al menos 6 horas de sol directo. Riegue la base sin mojar las hojas para evitar plagas y coloque un tutor (soporte) a medida que crezca.",
        )


class EstrategiaAlbahaca(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Albahaca"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio
        t_min = contexto.temperatura_min_promedio

        if 16.0 <= t_prom <= 27.0 and t_min >= 12.0:
            nivel = "Muy Recomendado"
            justificacion = f"Clima cálido/templado ideal para la albahaca (promedio {t_prom}°C). Estimula el crecimiento de hojas aromáticas tiernas."
        elif 10.0 <= t_prom < 16.0:
            nivel = "Recomendado"
            justificacion = f"El clima templado-frío ({t_prom}°C) ralentiza su crecimiento. Se aconseja cultivarla en macetas para poder resguardarla dentro de casa si bajan las temperaturas."
        else:
            nivel = "No Recomendado"
            justificacion = f"Las bajas temperaturas (mínima promedio de {t_min}°C) o el calor extremo marchitarán rápidamente la albahaca al aire libre."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=justificacion,
            consejos_cuidado="Prefiere riego frecuente manteniendo la tierra húmeda pero sin encharcar. Pellizque las puntas y retire las flores para promover más hojas.",
        )


class EstrategiaLechuga(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Lechuga"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio

        if 10.0 <= t_prom <= 20.0:
            nivel = "Muy Recomendado"
            justificacion = f"El rango de temperatura templado-frío ({t_prom}°C) es perfecto para la lechuga, evitando que se espigue (florezca prematuramente y se ponga amarga)."
        elif 20.0 < t_prom <= 25.0:
            nivel = "Recomendado"
            justificacion = f"Temperatura templada ({t_prom}°C). Se puede cultivar pero requiere sombra parcial durante las horas más cálidas del día para evitar que se deshidrate."
        else:
            nivel = "No Recomendado"
            justificacion = f"La temperatura promedio ({t_prom}°C) es inadecuada. Si es muy fría se hiela y si es muy cálida espigará casi de inmediato."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=justificacion,
            consejos_cuidado="Riego ligero pero frecuente para mantener la humedad superficial. Use suelos ricos en materia orgánica y coseche las hojas exteriores gradualmente.",
        )


class EstrategiaEspinaca(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Espinaca"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio

        if 8.0 <= t_prom <= 17.0:
            nivel = "Muy Recomendado"
            justificacion = f"Clima fresco ideal ({t_prom}°C). La espinaca soporta heladas ligeras y produce hojas tiernas y dulces en estas condiciones."
        elif 17.0 < t_prom <= 22.0:
            nivel = "Recomendado"
            justificacion = f"Temperatura de {t_prom}°C. Es posible cultivarla bajo la sombra de plantas más altas y manteniendo el suelo húmedo."
        else:
            nivel = "No Recomendado"
            justificacion = f"La temperatura promedio ({t_prom}°C) es demasiado alta. La espinaca entrará en floración muy rápido y sus hojas se volverán duras y amargas."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=justificacion,
            consejos_cuidado="Siembre en semisombra en climas intermedios. Mantenga el suelo fresco y húmedo mediante acolchado (mulch) orgánico.",
        )


class EstrategiaRomeroTomillo(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Romero y Tomillo"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio
        frec_lluvia = contexto.frecuencia_lluvia_pct

        if t_prom >= 14.0 and frec_lluvia <= 35.0:
            nivel = "Muy Recomendado"
            justificacion = f"Clima templado/cálido ({t_prom}°C) y con lluvias moderadas a secas ({frec_lluvia}%). Recrea las condiciones mediterráneas ideales para el romero y tomillo."
        elif t_prom >= 12.0:
            nivel = "Recomendado"
            justificacion = f"El romero tolerará el clima, pero debido a la frecuencia de lluvias del {frec_lluvia}%, se debe asegurar un sustrato muy poroso y con excelente drenaje en maceta."
        else:
            nivel = "No Recomendado"
            justificacion = f"El clima frío promedio ({t_prom}°C) y la alta humedad pueden pudrir las raíces del romero al aire libre. Intente cultivar en interiores bien iluminados."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=justificacion,
            consejos_cuidado="Riegue solo cuando la tierra esté completamente seca. Son plantas perennes que requieren mínimo mantenimiento una vez establecidas.",
        )


class EstrategiaMenta(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Menta"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio
        frec_lluvia = contexto.frecuencia_lluvia_pct

        if frec_lluvia >= 30.0 or t_prom <= 22.0:
            nivel = "Muy Recomendado"
            justificacion = f"La menta adora la humedad o el clima fresco/templado (promedio {t_prom}°C). Su crecimiento será vigoroso."
        else:
            nivel = "Recomendado"
            justificacion = f"Es una planta muy resistente que crecerá en clima seco ({frec_lluvia}% de lluvias), siempre y cuando el usuario se comprometa a regarla abundantemente."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Baja",
            justificacion=justificacion,
            consejos_cuidado="Se recomienda cultivarla en macetas individuales debido a su naturaleza invasiva. Tolera bien la semisombra y necesita riego frecuente.",
        )


class EstrategiaZanahoria(EstrategiaRecomendacion):
    @property
    def nombre(self) -> str:
        return "Zanahoria"

    def recomendar(self, contexto: ContextoRecomendacion) -> RecomendacionPlanta:
        t_prom = contexto.temperatura_promedio

        if 12.0 <= t_prom <= 22.0:
            nivel = "Muy Recomendado"
            justificacion = f"El rango de {t_prom}°C es óptimo para el desarrollo uniforme de la raíz de la zanahoria."
        elif 8.0 <= t_prom < 12.0 or 22.0 < t_prom <= 26.0:
            nivel = "Recomendado"
            justificacion = f"Las temperaturas promedio ({t_prom}°C) son viables, aunque en climas más cálidos las raíces pueden volverse fibrosas o cortas."
        else:
            nivel = "No Recomendado"
            justificacion = f"Las temperaturas extremas ({t_prom}°C promedio) dificultan la germinación y desarrollo de las raíces."

        return RecomendacionPlanta(
            nombre=self.nombre,
            nivel_recomendacion=nivel,
            dificultad="Media",
            justificacion=justificacion,
            consejos_cuidado="Requiere un suelo muy suelto y libre de piedras para que la raíz crezca recta. Mantenga una humedad constante durante la germinación.",
        )


def crear_estrategias_por_defecto() -> List[EstrategiaRecomendacion]:
    return [
        EstrategiaTomate(),
        EstrategiaAlbahaca(),
        EstrategiaLechuga(),
        EstrategiaEspinaca(),
        EstrategiaRomeroTomillo(),
        EstrategiaMenta(),
        EstrategiaZanahoria(),
    ]
