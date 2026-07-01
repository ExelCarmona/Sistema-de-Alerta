"""
app.py — Punto de entrada (Bootstrap)
Sistema de Clima y Recomendación de Cultivos
Arquitectura Hexagonal (Puertos y Adaptadores)
"""

import os
import sys
import streamlit as st

# Asegurarse de que el directorio raíz del proyecto esté en el path de Python
directorio_raiz = os.path.dirname(os.path.abspath(__file__))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

st.set_page_config(
    page_title="Sistema de Clima y Cultivos",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configuración global
RUTA_BD = os.path.join(directorio_raiz, "openmeteo_clima.db")

from adaptadores.sqlite_repository import RepositorioClimaSQLite
from adaptadores.openmeteo_api import AdaptadorApiOpenMeteo
from aplicacion.casos_uso.sincronizar_clima import CasoUsoSincronizarClima
from aplicacion.casos_uso.registrar_clima_manual import CasoUsoRegistrarClimaManual
from aplicacion.casos_uso.consultar_clima import CasoUsoConsultarClima
from aplicacion.casos_uso.obtener_recomendaciones import CasoUsoObtenerRecomendaciones
from dominio.reglas import MotorRecomendacion
from adaptadores.controladores.controlador_streamlit import arrancar_interfaz

@st.cache_resource
def inicializar_dependencias():
    """
    Inicializa los adaptadores y los inyecta en los casos de uso.
    Esto respeta el principio de desacoplamiento de la Arquitectura Hexagonal.
    """
    repositorio = RepositorioClimaSQLite(ruta_bd=RUTA_BD)
    api_externa = AdaptadorApiOpenMeteo()

    motor_recomendacion = MotorRecomendacion()

    return {
        "sincronizar": CasoUsoSincronizarClima(repositorio=repositorio, api_clima=api_externa),
        "registrar_manual": CasoUsoRegistrarClimaManual(repositorio=repositorio),
        "consultar": CasoUsoConsultarClima(repositorio=repositorio),
        "recomendaciones": CasoUsoObtenerRecomendaciones(repositorio=repositorio, motor_recomendacion=motor_recomendacion),
    }

# Iniciar aplicación
casos_uso = inicializar_dependencias()
arrancar_interfaz(casos_uso)
