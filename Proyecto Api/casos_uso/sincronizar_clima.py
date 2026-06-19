from puertos.repositorio import ClimaRepositoryPort
from puertos.api_clima import ClimaApiPort
from dominio.entidades import RegistroClimatico

class SincronizarClimaUseCase:
    """
    Caso de uso: Sincronizar Clima desde la API externa a la base de datos local.
    """
    def __init__(self, repositorio: ClimaRepositoryPort, api_clima: ClimaApiPort):
        self.repositorio = repositorio
        self.api_clima = api_clima

    def ejecutar(self, latitud: float, longitud: float) -> RegistroClimatico:
        # 1. Consultar el clima actual y pronósticos a la API externa
        registro = self.api_clima.obtener_clima(latitud, longitud)
        
        # 2. Persistir la localización (para obtener o actualizar el ID)
        localizacion_id = self.repositorio.guardar_localizacion(registro.localizacion)
        registro.localizacion.id = localizacion_id
        
        # 3. Asignar el ID de localización a los registros climáticos y persistir
        if registro.clima_actual:
            registro.clima_actual.localizacion_id = localizacion_id
            self.repositorio.guardar_clima_actual(registro.clima_actual)
            
        if registro.clima_horario:
            for item in registro.clima_horario:
                item.localizacion_id = localizacion_id
            self.repositorio.guardar_clima_horario(registro.clima_horario)
            
        if registro.clima_diario:
            for item in registro.clima_diario:
                item.localizacion_id = localizacion_id
            self.repositorio.guardar_clima_diario(registro.clima_diario)
            
        return registro
