"""
app.py
------
Punto de entrada principal para la aplicación de Turnos de Sábados.
Orquesta los componentes de cabecera, búsqueda reactiva, cuadrícula de sábados
y servicios de persistencia sin acoplamiento espagueti.
"""

import streamlit as st
import datetime
import os
import sys
import base64
import pandas as pd

# 0. Asegurar que el directorio raíz de la aplicación esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 1. Configuración de página de Streamlit
st.set_page_config(
    page_title="Turnos Sábados - Unión para la Salud y la Vida S.A.S",
    page_icon="img/LOGO.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inyección de Estilos Centralizados (100% en estilos/styles.py)
import importlib
from estilos import styles
importlib.reload(styles)
styles.apply_styles()

# Marcador para inicializar el Topbar sin saltos de layout
st.markdown('<div class="app-topbar-marker"></div>', unsafe_allow_html=True)

# 3. Servicios y Componentes Modulares
from modulos import procesador_datos as dp
from modulos import cliente_sharepoint as gc
from componentes import cabecera, buscador, cuadricula_turnos
importlib.reload(cabecera)
importlib.reload(buscador)
importlib.reload(cuadricula_turnos)
from componentes.cabecera import renderizar_cabecera, renderizar_banner_titulo, renderizar_aviso_informativo
from componentes.buscador import renderizar_buscador
from componentes.cuadricula_turnos import renderizar_cuadricula

# 4. Inicialización de Estado de Sesión (Session State)
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'last_load_time' not in st.session_state:
    st.session_state.last_load_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

if 'excel_path' not in st.session_state:
    import platform
    if gc.is_sharepoint_configured():
        st.session_state.excel_path = None
    elif platform.system() == "Windows":
        default_paths = [
            os.path.join(os.path.dirname(__file__), "CONSOLIDADO CONEXION.xlsx"),
            "CONSOLIDADO CONEXION.xlsx",
            os.path.join(os.path.dirname(__file__), "CONSOLIDADO 2026.xlsx"),
            "CONSOLIDADO 2026.xlsx",
            os.path.join(os.path.dirname(__file__), "TURNOS SABADOS.xlsx"),
            "TURNOS SABADOS.xlsx",
            r"c:\Users\JuanJoseOsorioMolina\Desktop\TURNOS SABADOS\TURNOS SABADOS.xlsx",
            r"C:\Users\JuanJoseOsorioMolina\OneDrive - U.T SAN VICENTE CES\TURNOS SABADOS.xlsx"
        ]
        st.session_state.excel_path = default_paths[0]
        for path in default_paths:
            if os.path.exists(path):
                st.session_state.excel_path = path
                break
    else:
        st.session_state.excel_path = None


def cargar_datos_app(reload_personal=False):
    """Carga y sincroniza los turnos y el directorio de supernumerarios."""
    try:
        df_shifts, errors = dp.load_data(st.session_state.excel_path)
        st.session_state.shifts_df = df_shifts
        st.session_state.errors = errors
        
        if reload_personal or 'super_df' not in st.session_state or st.session_state.super_df.empty:
            try:
                df_super = dp.load_supernumeraries(st.session_state.excel_path)
                st.session_state.super_df = df_super
                st.session_state.super_load_error = None
            except Exception as e_sup:
                st.session_state.super_df = pd.DataFrame()
                st.session_state.super_load_error = str(e_sup)
        
        st.session_state.data_loaded = True
        st.session_state.load_error = None
        st.session_state.last_load_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        st.session_state.shifts_df = pd.DataFrame()
        st.session_state.super_df = pd.DataFrame()
        st.session_state.errors = []
        st.session_state.data_loaded = False
        st.session_state.load_error = str(e)


if 'data_loaded' not in st.session_state or not st.session_state.data_loaded:
    cargar_datos_app()

if 'replacement_target' not in st.session_state:
    st.session_state.replacement_target = None
if 'last_action' not in st.session_state:
    st.session_state.last_action = None

# 5. Cargar Logo Institucional en Base64
logo_b64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo_union.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f_img:
        logo_b64 = base64.b64encode(f_img.read()).decode("utf-8")

# 6. Renderizar Cabecera y Topbar
renderizar_cabecera(logo_b64, cargar_datos_app)

# 7. Renderizar Banner de Título
renderizar_banner_titulo()

# Control de errores de carga de datos
if not st.session_state.data_loaded or st.session_state.load_error:
    st.error("### Error al cargar datos")
    st.info(f"Detalle: {st.session_state.load_error}")
    st.stop()

df_shifts = st.session_state.shifts_df
df_super = st.session_state.super_df

# Aviso informativo para usuarios en modo público (fuera de contenedores para evitar solapamientos)
if not st.session_state.is_admin:
    renderizar_aviso_informativo()

# 8. Contenedor Principal
with st.container():
    
    # Botón para deshacer último cambio (solo administradores)
    la = st.session_state.get('last_action')
    if st.session_state.is_admin and isinstance(la, dict):
        if st.button("Deshacer Último Movimiento", type="secondary", use_container_width=False, icon=":material/undo:", key="btn_deshacer_ultimo_cambio"):
            try:
                accion = str(la.get('action', ''))
                excel_p = str(la.get('excel_path', ''))
                hoja = str(la.get('sheet', ''))
                fecha = la.get('date')
                medico = str(la.get('doc', ''))
                obs = str(la.get('obs', ''))
                clasif = str(la.get('clasificacion', 'Secuencia Normal'))

                if accion in ['ELIMINAR', 'ELIMINAR_SIMPLE']:
                    dp.add_shift_to_date(excel_p, hoja, fecha, medico, obs, clasif)
                    st.success("Acción revertida: Médico re-agregado.")
                elif accion == 'ELIMINAR_LOTE':
                    shifts_to_restore = []
                    for item in la.get('deleted_items', []):
                        if isinstance(item, dict):
                            shifts_to_restore.append({
                                'sheet': item.get('sheet'),
                                'date': item.get('date'),
                                'doc': item.get('doc'),
                                'obs': item.get('obs'),
                                'clasificacion': item.get('clasificacion')
                            })
                    dp.add_shifts_batch(excel_p, shifts_to_restore)
                    st.success(f"Acción revertida: {len(shifts_to_restore)} asignaciones de turnos restauradas.")
                elif accion == 'AGREGAR':
                    dp.delete_shift_cell(excel_p, hoja, 0, 0, fecha, "", medico, clasif)
                    st.success("Acción revertida: Médico eliminado del día.")
                elif accion == 'MOVE':
                    nueva_fecha = la.get('new_date')
                    fecha_anterior = la.get('old_date')
                    dp.delete_shift_cell(excel_p, hoja, 0, 0, nueva_fecha, "", medico, clasif)
                    dp.add_shift_to_date(excel_p, hoja, fecha_anterior, medico, obs, clasif)
                    st.success("Acción revertida: Movimiento cancelado.")
                elif accion == 'REPLACE':
                    dp.update_shift_cell(
                        excel_path=excel_p,
                        sheet_name=hoja,
                        row_idx=int(la.get('row', 0)),
                        col_idx=int(la.get('col', 0)),
                        new_name=str(la.get('old_doc', '')),
                        date_val=fecha,
                        observation=str(la.get('old_obs', '')),
                        original_name=str(la.get('new_doc', '')),
                        clasificacion=str(la.get('old_clasif', 'Secuencia Normal'))
                    )
                    st.success("Acción revertida: Reemplazo / edición cancelado.")
                
                st.session_state.last_action = None
                cargar_datos_app()
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo deshacer: {e}")

    # 9. Buscador Centrado y Filtros Dinámicos
    termino_busqueda, filtro_activo = renderizar_buscador()

    # 10. Cuadrícula de Turnos (Admin / Público)
    renderizar_cuadricula(df_shifts, df_super, termino_busqueda, cargar_datos_app)

# 11. Footer Institucional
st.markdown("""
    <div class='app-footer'>
        © 2026 - Unión para la Salud y la Vida
    </div>
""", unsafe_allow_html=True)

# 12. Script de localización y supresión de elementos auxiliares de Streamlit Cloud
st.components.v1.html("""
    <script>
        try {
            window.parent.document.documentElement.lang = 'es';
            window.parent.document.body.classList.add('notranslate');
            const parentHead = window.parent.document.head;
            if (!parentHead.querySelector('meta[name="google"][content="notranslate"]')) {
                const meta = window.parent.document.createElement('meta');
                meta.name = 'google';
                meta.content = 'notranslate';
                parentHead.appendChild(meta);
            }
            if (!parentHead.querySelector('#hide-badge-style')) {
                const style = window.parent.document.createElement('style');
                style.id = 'hide-badge-style';
                style.innerHTML = `
                    div[class*="viewerBadge_container"], 
                    [class^="viewerBadge_container"],
                    .viewerBadge_container,
                    [data-testid="viewerBadge"],
                    [data-testid="stAppDeployButton"],
                    [data-testid="stSidebar"],
                    section[data-testid="stSidebar"],
                    [data-testid="collapsedControl"] {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
                        width: 0px !important;
                    }
                `;
                parentHead.appendChild(style);
            }
        } catch (e) {
            console.error("Parent override failed:", e);
        }
    </script>
""", height=0, width=0)