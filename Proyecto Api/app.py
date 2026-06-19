"""
app.py — Adaptador Primario (Interfaz de Usuario con Streamlit)
Sistema de Clima y Recomendación de Cultivos
Arquitectura Hexagonal (Puertos y Adaptadores)
"""

import streamlit as st
import os
import sys

# Asegurarse de que el directorio raíz del proyecto esté en el path de Python
directorio_raiz = os.path.dirname(os.path.abspath(__file__))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

from adaptadores.sqlite_repository import SQLiteClimaRepository
from adaptadores.openmeteo_api import OpenMeteoApiAdapter
from casos_uso.sincronizar_clima import SincronizarClimaUseCase
from casos_uso.registrar_clima_manual import RegistrarClimaManualUseCase
from casos_uso.consultar_clima import ConsultarClimaUseCase
from casos_uso.obtener_recomendaciones import ObtenerRecomendacionesUseCase
from dominio.entidades import Localizacion, ClimaActual, ClimaHorario, ClimaDiario

# ─────────────────────────────────────────
#  CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────
DB_PATH = os.path.join(directorio_raiz, "openmeteo_clima.db")

st.set_page_config(
    page_title="Sistema de Clima y Cultivos",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  ESTILOS CSS PERSONALIZADOS
# ─────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Fondo degradado general */
  .stApp {
    background: linear-gradient(135deg, #0f1923 0%, #1a2d3d 50%, #0f2027 100%);
    color: #e8f4f8;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f2d 0%, #1b3a4b 100%);
    border-right: 1px solid rgba(56,189,248,0.15);
  }
  section[data-testid="stSidebar"] .stRadio label {
    color: #94d3e8 !important;
    font-weight: 500;
  }

  /* Tarjetas generales */
  .card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(56,189,248,0.15);
  }

  /* Tarjeta clima actual */
  .clima-card {
    background: linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(6,182,212,0.08) 100%);
    border: 1px solid rgba(14,165,233,0.30);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
  }
  .clima-temp {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
  }
  .clima-label {
    font-size: 0.85rem;
    color: #7dd3fc;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.25rem;
  }

  /* Tarjetas de recomendación */
  .rec-card-verde {
    background: linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,150,105,0.08) 100%);
    border: 1px solid rgba(16,185,129,0.35);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: transform 0.2s ease;
  }
  .rec-card-verde:hover { transform: translateY(-3px); }

  .rec-card-amarilla {
    background: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(217,119,6,0.08) 100%);
    border: 1px solid rgba(245,158,11,0.35);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: transform 0.2s ease;
  }
  .rec-card-amarilla:hover { transform: translateY(-3px); }

  .rec-card-roja {
    background: linear-gradient(135deg, rgba(239,68,68,0.10) 0%, rgba(185,28,28,0.05) 100%);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    opacity: 0.75;
    transition: transform 0.2s ease;
  }
  .rec-card-roja:hover { transform: translateY(-3px); }

  .rec-nombre {
    font-size: 1.2rem;
    font-weight: 700;
    color: #f0faf5;
    margin-bottom: 0.25rem;
  }
  .badge-verde {
    background: rgba(16,185,129,0.25);
    color: #34d399;
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 999px;
    padding: 0.15rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.6rem;
  }
  .badge-amarilla {
    background: rgba(245,158,11,0.20);
    color: #fbbf24;
    border: 1px solid rgba(251,191,36,0.4);
    border-radius: 999px;
    padding: 0.15rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.6rem;
  }
  .badge-roja {
    background: rgba(239,68,68,0.15);
    color: #f87171;
    border: 1px solid rgba(248,113,113,0.4);
    border-radius: 999px;
    padding: 0.15rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.6rem;
  }
  .rec-text {
    color: #c7dfe8;
    font-size: 0.88rem;
    line-height: 1.5;
  }
  .consejos-label {
    color: #7dd3fc;
    font-weight: 600;
    font-size: 0.8rem;
    margin-top: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  /* Stat chips */
  .stat-chip {
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.20);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    text-align: center;
  }
  .stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #38bdf8;
    line-height: 1.1;
  }
  .stat-label {
    font-size: 0.75rem;
    color: #90c5d8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  /* Título principal */
  .titulo-principal {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #67e8f9, #a5f3fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
  }
  .subtitulo {
    color: #64a8be;
    font-size: 0.95rem;
    margin-bottom: 2rem;
  }

  /* Botones */
  .stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #06b6d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(14,165,233,0.3) !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14,165,233,0.4) !important;
  }

  /* Inputs */
  .stNumberInput input, .stTextInput input, .stSelectbox select, .stDateInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 8px !important;
    color: #e8f4f8 !important;
  }
  label { color: #94d3e8 !important; }

  /* Dividers */
  hr { border-color: rgba(56,189,248,0.15) !important; }

  /* Success / Info / Error boxes */
  .stSuccess { background-color: rgba(16,185,129,0.1) !important; border-color: #10b981 !important; }
  .stInfo { background-color: rgba(14,165,233,0.1) !important; border-color: #0ea5e9 !important; }
  .stError { background-color: rgba(239,68,68,0.1) !important; border-color: #ef4444 !important; }

  /* Sidebar título */
  .sidebar-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 0.25rem;
  }
  .sidebar-subtitle {
    font-size: 0.8rem;
    color: #64a8be;
    margin-bottom: 1.5rem;
  }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
#  INYECCIÓN DE DEPENDENCIAS
# ─────────────────────────────────────────
@st.cache_resource
def inicializar_dependencias():
    """
    Inicializa los adaptadores y los inyecta en los casos de uso.
    Esto respeta el principio de desacoplamiento de la Arquitectura Hexagonal.
    """
    repositorio = SQLiteClimaRepository(db_path=DB_PATH)
    api_externa = OpenMeteoApiAdapter()

    return {
        "sincronizar": SincronizarClimaUseCase(repositorio=repositorio, api_clima=api_externa),
        "registrar_manual": RegistrarClimaManualUseCase(repositorio=repositorio),
        "consultar": ConsultarClimaUseCase(repositorio=repositorio),
        "recomendaciones": ObtenerRecomendacionesUseCase(repositorio=repositorio),
    }

deps = inicializar_dependencias()

# ─────────────────────────────────────────
#  SIDEBAR — Navegación
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🌿 ClimaJardín</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">Sistema de Clima y Cultivos · Arquitectura Hexagonal</div>', unsafe_allow_html=True)
    st.divider()

    seccion = st.radio(
        "Navegación",
        options=[
            "📊 Dashboard de Clima",
            "🌐 Sincronizar desde API",
            "✍️ Registro Manual",
            "🌱 Recomendaciones de Cultivo",
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown(
        '<p style="font-size:0.72rem;color:#4a7a8a;line-height:1.5;">'
        '🔗 Datos climáticos provistos por <a href="https://open-meteo.com/" style="color:#38bdf8;">Open-Meteo</a><br>'
        '🗄️ Base de datos: <code style="color:#67e8f9;">openmeteo_clima.db</code><br>'
        '🏗️ Arquitectura Hexagonal + POO</p>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────
#  FUNCIONES AUXILIARES DE RENDER
# ─────────────────────────────────────────
CODIGOS_CLIMA = {
    0: "☀️ Despejado", 1: "🌤️ Mayormente despejado", 2: "⛅ Parcialmente nublado",
    3: "☁️ Nublado", 45: "🌫️ Neblina", 48: "🌫️ Niebla helada",
    51: "🌦️ Llovizna ligera", 53: "🌦️ Llovizna moderada", 55: "🌧️ Llovizna densa",
    61: "🌧️ Lluvia ligera", 63: "🌧️ Lluvia moderada", 65: "🌧️ Lluvia intensa",
    71: "❄️ Nevada ligera", 73: "❄️ Nevada moderada", 75: "❄️ Nevada intensa",
    80: "🌦️ Chubascos ligeros", 81: "🌦️ Chubascos moderados", 82: "🌩️ Chubascos violentos",
    95: "⛈️ Tormenta", 96: "⛈️ Tormenta con granizo", 99: "⛈️ Tormenta con granizo fuerte",
}

def describir_codigo(codigo):
    if codigo is None:
        return "Desconocido"
    return CODIGOS_CLIMA.get(int(codigo), f"Código {codigo}")


def formatear_etiqueta_localizacion(loc):
    zona = loc.zona_horaria or "?"
    return f"📍 Lat {loc.latitud:.4f} / Lon {loc.longitud:.4f} — {zona} (ID {loc.id})"


# ═══════════════════════════════════════════════════════
#  SECCIÓN 1: DASHBOARD DE CLIMA
# ═══════════════════════════════════════════════════════
if seccion == "📊 Dashboard de Clima":
    st.markdown('<div class="titulo-principal">📊 Dashboard de Clima</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Visualiza el historial climático guardado en la base de datos local.</div>', unsafe_allow_html=True)

    localizaciones = deps["consultar"].obtener_localizaciones()

    if not localizaciones:
        st.info("⚠️ No hay localizaciones guardadas. Ve a **Sincronizar desde API** para importar tu primera ubicación.")
    else:
        opciones = {formatear_etiqueta_localizacion(loc): loc.id for loc in localizaciones}
        seleccion = st.selectbox("Selecciona una Localización", options=list(opciones.keys()))
        loc_id = opciones[seleccion]

        registro = deps["consultar"].obtener_registro_completo(loc_id, limite_horas=168, limite_dias=14)

        if registro:
            loc = registro.localizacion

            # — Tarjeta Clima Actual —
            if registro.clima_actual:
                ca = registro.clima_actual
                st.markdown("### 🌡️ Clima Actual")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown(
                        f'<div class="clima-card">'
                        f'<div class="clima-label">Temperatura</div>'
                        f'<div class="clima-temp">{ca.temperatura_2m if ca.temperatura_2m is not None else "—"}°C</div>'
                        f'</div>', unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f'<div class="clima-card">'
                        f'<div class="clima-label">Humedad</div>'
                        f'<div class="clima-temp" style="font-size:2.5rem;">{ca.humedad_relativa_2m if ca.humedad_relativa_2m is not None else "—"}%</div>'
                        f'</div>', unsafe_allow_html=True
                    )
                with c3:
                    st.markdown(
                        f'<div class="clima-card">'
                        f'<div class="clima-label">Viento</div>'
                        f'<div class="clima-temp" style="font-size:2.2rem;">{ca.velocidad_viento_10m if ca.velocidad_viento_10m is not None else "—"}<span style="font-size:1rem;"> km/h</span></div>'
                        f'</div>', unsafe_allow_html=True
                    )
                with c4:
                    st.markdown(
                        f'<div class="clima-card">'
                        f'<div class="clima-label">Condición</div>'
                        f'<div style="font-size:1.1rem;color:#e8f4f8;font-weight:600;margin-top:0.5rem;">{describir_codigo(ca.codigo_clima)}</div>'
                        f'<div style="font-size:0.78rem;color:#64a8be;margin-top:0.25rem;">{ca.tiempo}</div>'
                        f'</div>', unsafe_allow_html=True
                    )

            st.markdown("---")

            # — Gráficas Históricas —
            col_graf1, col_graf2 = st.columns(2)

            with col_graf1:
                st.markdown("#### 🌡️ Temperatura Horaria (últimas 168 horas)")
                if registro.clima_horario:
                    import datetime
                    tiempos = [r.tiempo for r in registro.clima_horario]
                    temps = [r.temperatura_2m for r in registro.clima_horario]
                    # Filtramos nulos
                    datos = [(t, v) for t, v in zip(tiempos, temps) if v is not None]
                    if datos:
                        import streamlit as st2
                        chart_data = {"Hora": [d[0] for d in datos], "Temperatura (°C)": [d[1] for d in datos]}
                        st.line_chart(
                            data={k: v for k, v in chart_data.items() if k != "Hora"},
                            use_container_width=True,
                            color=["#38bdf8"]
                        )
                    else:
                        st.caption("Sin datos de temperatura horaria disponibles.")
                else:
                    st.caption("No hay registros horarios guardados para esta localización.")

            with col_graf2:
                st.markdown("#### 🌧️ Precipitación Diaria")
                if registro.clima_diario:
                    fechas = [r.fecha for r in registro.clima_diario]
                    lluvias = [r.suma_precipitacion if r.suma_precipitacion is not None else 0 for r in registro.clima_diario]
                    st.bar_chart(
                        data={"Precipitación (mm)": lluvias},
                        use_container_width=True,
                        color=["#06b6d4"]
                    )
                else:
                    st.caption("No hay registros diarios guardados para esta localización.")

            st.markdown("---")

            # — Tabla Resumen Diario —
            st.markdown("#### 📅 Resumen Climático Diario")
            if registro.clima_diario:
                import pandas as pd
                filas = []
                for d in registro.clima_diario:
                    filas.append({
                        "Fecha": d.fecha,
                        "Cond.": describir_codigo(d.codigo_clima_max),
                        "Máx (°C)": d.temperatura_2m_max,
                        "Mín (°C)": d.temperatura_2m_min,
                        "Precipitación (mm)": d.suma_precipitacion,
                    })
                df = pd.DataFrame(filas)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("No hay registros diarios guardados.")


# ═══════════════════════════════════════════════════════
#  SECCIÓN 2: SINCRONIZAR DESDE API
# ═══════════════════════════════════════════════════════
elif seccion == "🌐 Sincronizar desde API":
    st.markdown('<div class="titulo-principal">🌐 Sincronizar desde Open-Meteo</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Consulta el clima en tiempo real de cualquier coordenada y guárdalo automáticamente en la base de datos.</div>', unsafe_allow_html=True)

    with st.form("formulario_api"):
        st.markdown("#### 📍 Coordenadas de Búsqueda")
        c1, c2 = st.columns(2)
        with c1:
            latitud = st.number_input("Latitud", value=19.4326, min_value=-90.0, max_value=90.0, format="%.6f",
                                       help="Ej: 19.4326 = Ciudad de México")
        with c2:
            longitud = st.number_input("Longitud", value=-99.1332, min_value=-180.0, max_value=180.0, format="%.6f",
                                        help="Ej: -99.1332 = Ciudad de México")

        submitted = st.form_submit_button("🔄 Consultar y Sincronizar con Open-Meteo", use_container_width=True)

    if submitted:
        with st.spinner("⏳ Conectando con la API de Open-Meteo y guardando datos..."):
            try:
                registro = deps["sincronizar"].ejecutar(latitud=latitud, longitud=longitud)
                st.success(f"✅ ¡Datos sincronizados exitosamente para Lat: **{registro.localizacion.latitud}** / Lon: **{registro.localizacion.longitud}**!")

                # Mostrar resultado
                st.markdown("#### 🌡️ Resultado del Pronóstico Importado")
                loc = registro.localizacion
                ca = registro.clima_actual

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(
                        f'<div class="card">'
                        f'<div class="clima-label">📍 Localización</div>'
                        f'<div style="font-weight:600;font-size:1rem;color:#e8f4f8;margin-top:0.5rem;">'
                        f'Lat {loc.latitud:.4f} / Lon {loc.longitud:.4f}</div>'
                        f'<div style="color:#64a8be;font-size:0.85rem;">{loc.zona_horaria or ""}</div>'
                        f'<div style="color:#64a8be;font-size:0.85rem;">Elevación: {loc.elevacion or "—"} m</div>'
                        f'</div>', unsafe_allow_html=True
                    )
                with col2:
                    if ca:
                        st.markdown(
                            f'<div class="clima-card">'
                            f'<div class="clima-label">Temperatura Actual</div>'
                            f'<div class="clima-temp">{ca.temperatura_2m}°C</div>'
                            f'<div style="color:#67e8f9;font-size:0.9rem;margin-top:0.4rem;">{describir_codigo(ca.codigo_clima)}</div>'
                            f'</div>', unsafe_allow_html=True
                        )
                with col3:
                    if ca:
                        st.markdown(
                            f'<div class="card" style="text-align:center;">'
                            f'<div class="clima-label">Humedad / Viento</div>'
                            f'<div style="font-size:1.8rem;font-weight:700;color:#67e8f9;">{ca.humedad_relativa_2m}%</div>'
                            f'<div style="color:#94d3e8;font-size:0.85rem;">💨 {ca.velocidad_viento_10m} km/h</div>'
                            f'</div>', unsafe_allow_html=True
                        )

                st.markdown(f"**📦 Registros importados:** `{len(registro.clima_horario)}` horarios · `{len(registro.clima_diario)}` diarios")

                # Vista previa de días
                if registro.clima_diario:
                    st.markdown("#### 📅 Vista Previa — Pronóstico Diario")
                    import pandas as pd
                    filas = []
                    for d in registro.clima_diario:
                        filas.append({
                            "Fecha": d.fecha,
                            "Condición": describir_codigo(d.codigo_clima_max),
                            "Máx (°C)": d.temperatura_2m_max,
                            "Mín (°C)": d.temperatura_2m_min,
                            "Precipitación (mm)": d.suma_precipitacion,
                        })
                    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

            except RuntimeError as e:
                st.error(f"❌ Error de conexión con Open-Meteo: {e}")
            except Exception as e:
                st.error(f"❌ Error inesperado: {e}")

    else:
        st.markdown(
            '<div class="card">'
            '<p style="color:#64a8be;text-align:center;margin:0;">'
            '🌍 Ingresa las coordenadas de cualquier ubicación del mundo y el sistema consultará '
            'el pronóstico de 7 días de Open-Meteo, guardando automáticamente todos los registros '
            'en <code>openmeteo_clima.db</code>.'
            '</p></div>',
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════
#  SECCIÓN 3: REGISTRO MANUAL
# ═══════════════════════════════════════════════════════
elif seccion == "✍️ Registro Manual":
    st.markdown('<div class="titulo-principal">✍️ Registro Climático Manual</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Agrega o actualiza registros climáticos directamente en la base de datos respetando la estructura original.</div>', unsafe_allow_html=True)

    tipo_registro = st.tabs(["📍 Nueva Localización", "🌡️ Clima Actual", "🕐 Clima Horario", "📅 Clima Diario"])

    # ── TAB 1: Nueva Localización ──
    with tipo_registro[0]:
        st.markdown("#### Registrar Nueva Localización")
        with st.form("form_localizacion"):
            c1, c2 = st.columns(2)
            with c1:
                lat_m = st.number_input("Latitud *", value=20.9670, format="%.6f")
                zona_m = st.text_input("Zona Horaria", value="America/Mexico_City", placeholder="Ej: Europe/Madrid")
            with c2:
                lon_m = st.number_input("Longitud *", value=-89.6237, format="%.6f")
                utc_off = st.number_input("UTC Offset (segundos)", value=-18000)
            elev_m = st.number_input("Elevación (m)", value=10.0, format="%.1f")
            sub = st.form_submit_button("💾 Guardar Localización", use_container_width=True)

        if sub:
            try:
                loc = Localizacion(latitud=lat_m, longitud=lon_m, elevacion=elev_m, zona_horaria=zona_m or None, utc_offset_segundos=int(utc_off))
                new_id = deps["registrar_manual"].registrar_localizacion(loc)
                st.success(f"✅ Localización guardada/actualizada con ID: **{new_id}**")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ── TAB 2: Clima Actual ──
    with tipo_registro[1]:
        st.markdown("#### Registrar / Actualizar Clima Actual")
        localizaciones = deps["consultar"].obtener_localizaciones()
        if not localizaciones:
            st.warning("⚠️ Primero registra una localización en la pestaña 'Nueva Localización'.")
        else:
            opciones = {formatear_etiqueta_localizacion(l): l.id for l in localizaciones}
            with st.form("form_clima_actual"):
                sel_loc = st.selectbox("Localización *", options=list(opciones.keys()))
                c1, c2 = st.columns(2)
                with c1:
                    tiempo_a = st.text_input("Tiempo (ISO 8601) *", value="2026-06-19T10:00", placeholder="YYYY-MM-DDTHH:MM")
                    temp_a = st.number_input("Temperatura 2m (°C)", value=22.0, format="%.1f")
                    hum_a = st.number_input("Humedad Relativa (%)", value=60.0, min_value=0.0, max_value=100.0, format="%.1f")
                with c2:
                    cod_a = st.number_input("Código de Clima", value=0, min_value=0, max_value=99, step=1)
                    viento_a = st.number_input("Velocidad de Viento 10m (km/h)", value=10.0, format="%.1f")
                sub_a = st.form_submit_button("💾 Guardar Clima Actual", use_container_width=True)

            if sub_a:
                try:
                    ca = ClimaActual(
                        tiempo=tiempo_a, temperatura_2m=temp_a, humedad_relativa_2m=hum_a,
                        codigo_clima=cod_a, velocidad_viento_10m=viento_a,
                        localizacion_id=opciones[sel_loc]
                    )
                    deps["registrar_manual"].registrar_clima_actual(ca)
                    st.success("✅ Clima actual guardado correctamente.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # ── TAB 3: Clima Horario ──
    with tipo_registro[2]:
        st.markdown("#### Registrar Dato de Clima Horario")
        localizaciones = deps["consultar"].obtener_localizaciones()
        if not localizaciones:
            st.warning("⚠️ Primero registra una localización.")
        else:
            opciones = {formatear_etiqueta_localizacion(l): l.id for l in localizaciones}
            with st.form("form_clima_horario"):
                sel_loc_h = st.selectbox("Localización *", options=list(opciones.keys()))
                c1, c2 = st.columns(2)
                with c1:
                    tiempo_h = st.text_input("Tiempo *", value="2026-06-19T12:00", placeholder="YYYY-MM-DDTHH:MM")
                    temp_h = st.number_input("Temperatura 2m (°C)", value=25.0, format="%.1f")
                    prob_h = st.number_input("Probabilidad Precipitación (%)", value=0.0, min_value=0.0, max_value=100.0, format="%.1f")
                with c2:
                    precip_h = st.number_input("Precipitación (mm)", value=0.0, format="%.2f")
                    cod_h = st.number_input("Código de Clima", value=0, min_value=0, max_value=99, step=1)
                sub_h = st.form_submit_button("💾 Guardar Clima Horario", use_container_width=True)

            if sub_h:
                try:
                    ch = ClimaHorario(
                        tiempo=tiempo_h, temperatura_2m=temp_h, probabilidad_precipitacion=prob_h,
                        precipitacion=precip_h, codigo_clima=cod_h, localizacion_id=opciones[sel_loc_h]
                    )
                    deps["registrar_manual"].registrar_clima_horario(ch)
                    st.success(f"✅ Registro horario para `{tiempo_h}` guardado correctamente.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # ── TAB 4: Clima Diario ──
    with tipo_registro[3]:
        st.markdown("#### Registrar Dato de Clima Diario")
        localizaciones = deps["consultar"].obtener_localizaciones()
        if not localizaciones:
            st.warning("⚠️ Primero registra una localización.")
        else:
            opciones = {formatear_etiqueta_localizacion(l): l.id for l in localizaciones}
            with st.form("form_clima_diario"):
                sel_loc_d = st.selectbox("Localización *", options=list(opciones.keys()))
                c1, c2 = st.columns(2)
                with c1:
                    fecha_d = st.date_input("Fecha *")
                    cod_max_d = st.number_input("Código de Clima Máx", value=1, min_value=0, max_value=99, step=1)
                    temp_max_d = st.number_input("Temperatura Máxima (°C)", value=28.0, format="%.1f")
                with c2:
                    temp_min_d = st.number_input("Temperatura Mínima (°C)", value=15.0, format="%.1f")
                    precip_d = st.number_input("Suma Precipitación (mm)", value=0.0, format="%.2f")
                sub_d = st.form_submit_button("💾 Guardar Clima Diario", use_container_width=True)

            if sub_d:
                try:
                    cd = ClimaDiario(
                        fecha=str(fecha_d), codigo_clima_max=cod_max_d,
                        temperatura_2m_max=temp_max_d, temperatura_2m_min=temp_min_d,
                        suma_precipitacion=precip_d, localizacion_id=opciones[sel_loc_d]
                    )
                    deps["registrar_manual"].registrar_clima_diario(cd)
                    st.success(f"✅ Registro diario para `{fecha_d}` guardado correctamente.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")


# ═══════════════════════════════════════════════════════
#  SECCIÓN 4: RECOMENDACIONES DE CULTIVO
# ═══════════════════════════════════════════════════════
elif seccion == "🌱 Recomendaciones de Cultivo":
    st.markdown('<div class="titulo-principal">🌱 Recomendaciones de Cultivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">El motor de reglas analiza el historial climático guardado y sugiere qué plantas domésticas sembrar en tu jardín.</div>', unsafe_allow_html=True)

    localizaciones = deps["consultar"].obtener_localizaciones()

    if not localizaciones:
        st.info("⚠️ No hay localizaciones con datos climáticos. Ve a **Sincronizar desde API** para importar datos primero.")
    else:
        opciones = {formatear_etiqueta_localizacion(loc): loc.id for loc in localizaciones}
        c1, c2 = st.columns([3, 1])
        with c1:
            seleccion = st.selectbox("Selecciona una Localización para analizar", options=list(opciones.keys()))
        with c2:
            limite = st.number_input("Días a analizar", value=14, min_value=1, max_value=90)

        loc_id = opciones[seleccion]

        if st.button("🔍 Analizar y Generar Recomendaciones", use_container_width=False):
            resultado = deps["recomendaciones"].ejecutar(localizacion_id=loc_id, limite_dias=int(limite))

            if not resultado["recomendaciones"]:
                st.warning("⚠️ No hay suficientes registros diarios para esta localización. Sincroniza primero los datos desde la API.")
            else:
                stats = resultado["estadisticas"]

                # — Estadísticas Climáticas —
                st.markdown("### 📊 Análisis Climático de la Zona")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.markdown(f'<div class="stat-chip"><div class="stat-value">{stats["temperatura_promedio"]}°C</div><div class="stat-label">Temp. Promedio</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="stat-chip"><div class="stat-value">{stats["temperatura_max_promedio"]}°C</div><div class="stat-label">Temp. Máx. Prom.</div></div>', unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div class="stat-chip"><div class="stat-value">{stats["temperatura_min_promedio"]}°C</div><div class="stat-label">Temp. Mín. Prom.</div></div>', unsafe_allow_html=True)
                with col4:
                    st.markdown(f'<div class="stat-chip"><div class="stat-value">{stats["frecuencia_lluvia_pct"]}%</div><div class="stat-label">Días con Lluvia</div></div>', unsafe_allow_html=True)
                with col5:
                    st.markdown(f'<div class="stat-chip"><div class="stat-value">{stats["total_lluvia"]} mm</div><div class="stat-label">Lluvia Total</div></div>', unsafe_allow_html=True)

                st.markdown("")
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"🌡️ **Clasificación Temperatura:** {stats['clasificacion_temperatura']}")
                with c2:
                    st.info(f"🌧️ **Clasificación Lluvia:** {stats['clasificacion_lluvia']}")

                st.markdown("---")
                st.markdown("### 🌿 Plantas Recomendadas para tu Jardín")

                # — Tarjetas de Recomendación —
                ICONOS_PLANTAS = {
                    "Tomate": "🍅", "Albahaca": "🌿", "Lechuga": "🥬",
                    "Espinaca": "🫛", "Romero y Tomillo": "🌱", "Menta": "🍃", "Zanahoria": "🥕"
                }
                ESTILOS_NIVEL = {
                    "Muy Recomendado":  ("rec-card-verde",   "badge-verde",   "✅ Muy Recomendado"),
                    "Recomendado":      ("rec-card-amarilla", "badge-amarilla", "⚡ Recomendado"),
                    "No Recomendado":   ("rec-card-roja",    "badge-roja",    "❌ No Recomendado"),
                }

                for rec in resultado["recomendaciones"]:
                    card_cls, badge_cls, badge_text = ESTILOS_NIVEL.get(
                        rec.nivel_recomendacion, ("card", "badge-verde", rec.nivel_recomendacion)
                    )
                    icono = ICONOS_PLANTAS.get(rec.nombre, "🌱")
                    st.markdown(
                        f'<div class="{card_cls}">'
                        f'<div class="rec-nombre">{icono} {rec.nombre}</div>'
                        f'<span class="{badge_cls}">{badge_text}</span> '
                        f'<span style="color:#64a8be;font-size:0.8rem;">Dificultad: {rec.dificultad}</span>'
                        f'<p class="rec-text">{rec.justificacion}</p>'
                        f'<div class="consejos-label">🪴 Consejos de cuidado</div>'
                        f'<p class="rec-text">{rec.consejos_cuidado}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
