from aplicacion.puertos.repositorio import PuertoRepositorioClima
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario

class CasoUsoRegistrarClimaManual:
    """
    Caso de uso: Registrar manualmente datos climáticos en la base de datos SQLite,
    asegurando que se respeten los tipos y constraints originales.
    """
    def __init__(self, repositorio: PuertoRepositorioClima):
        self.repositorio = repositorio

    def registrar_localizacion(self, localizacion: Localizacion) -> int:
        """
        Registra una nueva ubicación manual o retorna el ID si ya existe.
        """
        if not localizacion.latitud or not localizacion.longitud:
            raise ValueError("La latitud y longitud son obligatorias.")
        return self.repositorio.guardar_localizacion(localizacion)

    def registrar_clima_actual(self, clima: ClimaActual) -> None:
        """
        Guarda o sobreescribe un registro de Clima Actual manual.
        """
        if not clima.id_localizacion:
            raise ValueError("Se requiere asignar una localización al clima actual.")
        if not clima.tiempo:
            raise ValueError("El tiempo (fecha/hora) es obligatorio.")
        
        self.repositorio.guardar_clima_actual(clima)

    def registrar_clima_horario(self, clima: ClimaHorario) -> None:
        """
        Guarda o sobreescribe un registro de Clima Horario manual.
        """
        if not clima.id_localizacion:
            raise ValueError("Se requiere asignar una localización al clima horario.")
        if not clima.tiempo:
            raise ValueError("El tiempo (fecha/hora) es obligatorio.")
        
        self.repositorio.guardar_clima_horario([clima])

    def registrar_clima_diario(self, clima: ClimaDiario) -> None:
        """
        Guarda o sobreescribe un registro de Clima Diario manual.
        """
        if not clima.id_localizacion:
            raise ValueError("Se requiere asignar una localización al clima diario.")
        if not clima.fecha:
            raise ValueError("La fecha es obligatoria.")
        
        self.repositorio.guardar_clima_diario([clima])
