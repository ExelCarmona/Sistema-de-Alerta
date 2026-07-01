from aplicacion.puertos.repositorio import PuertoRepositorioClima
from aplicacion.puertos.api_clima import PuertoApiClima
from dominio.entidades import RegistroClimatico

class CasoUsoSincronizarClima:
    """
    Caso de uso: Sincronizar Clima desde la API externa a la base de datos local.
    """
    def __init__(self, repositorio: PuertoRepositorioClima, api_clima: PuertoApiClima):
        self.repositorio = repositorio
        self.api_clima = api_clima

    def ejecutar(self, latitud: float, longitud: float) -> RegistroClimatico:
        # 1. Consultar el clima actual y pronósticos a la API externa
        registro = self.api_clima.obtener_clima(latitud, longitud)
        
        # 2. Persistir la localización (para obtener o actualizar el ID)
        id_localizacion = self.repositorio.guardar_localizacion(registro.localizacion)
        registro.localizacion.id = id_localizacion
        
        # 3. Asignar el ID de localización a los registros climáticos y persistir
        if registro.clima_actual:
            registro.clima_actual.id_localizacion = id_localizacion
            self.repositorio.guardar_clima_actual(registro.clima_actual)
            
        if registro.clima_horario:
            for item in registro.clima_horario:
                item.id_localizacion = id_localizacion
            self.repositorio.guardar_clima_horario(registro.clima_horario)
            
        if registro.clima_diario:
            for item in registro.clima_diario:
                item.id_localizacion = id_localizacion
            self.repositorio.guardar_clima_diario(registro.clima_diario)
            
        return registro
