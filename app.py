# pyrefly: ignore [missing-import]
# Actualización forzada del layout
import streamlit as st
import pandas as pd
import datetime
import os
import re
import data_processor as dp
import styles
import importlib
importlib.reload(styles)
import ui_dialogs
import graph_client as gc
import base64

# Set page config for Streamlit
st.set_page_config(
    page_title="TURNOS SABADOS DE LOS SUPERNUMERARIOS",
    page_icon="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/calendar3.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom premium styles
styles.apply_styles()

# ----------------- SESSION STATE & CACHING -----------------

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'last_load_time' not in st.session_state:
    st.session_state.last_load_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

if 'excel_path' not in st.session_state:
    # En modo SharePoint no se usa ruta local para los archivos delta.
    # Se mantiene solo como referencia para compatibilidad con data_processor.
    import platform
    if gc.is_sharepoint_configured():
        # Conexión directa al archivo de SharePoint vía Microsoft Graph API
        st.session_state.excel_path = None
    elif platform.system() == "Windows":
        # Ejecución local como fallback solo si no hay credenciales SharePoint
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

# Function to load and clean data
def load_app_data(reload_personal=False):
    try:
        # Load Saturday shifts
        df_shifts, errors = dp.load_data(st.session_state.excel_path)
        st.session_state.shifts_df = df_shifts
        st.session_state.errors = errors
        
        # Load Supernumeraries directory solo en inicio o sincronización explícita
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
    load_app_data()

# Initialize session state for replacement flow
if 'replacement_target' not in st.session_state:
    st.session_state.replacement_target = None
if 'last_action' not in st.session_state:
    st.session_state.last_action = None



# ----------------- MAIN APP INTERFACE -----------------

# ----------------- TOPBAR INSTITUCIONAL -----------------
# Cargar imagen oficial de logo en base64 para renderizado instantáneo
logo_b64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo_union.png")
if os.path.exists(logo_path):
    import base64
    with open(logo_path, "rb") as f_img:
        logo_b64 = base64.b64encode(f_img.read()).decode("utf-8")

# Inyección directa de estilos clave del Topbar para garantizar sincronización inmediata
st.markdown("""
<style>
:root { --usv-user-initials: "JJ"; }
.app-topbar-marker { display: none !important; }

/* Eliminar por completo el espacio superior del contenedor principal de Streamlit */
header[data-testid="stHeader"],
[data-testid="stHeader"] {
    display: none !important;
    height: 0px !important;
    min-height: 0px !important;
    max-height: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
    visibility: hidden !important;
}

.stApp,
[data-testid="stAppViewContainer"],
section.main,
.stMain,
div[data-testid="stMain"],
div[data-testid="stMainBlockContainer"],
.stMainBlockContainer,
.block-container {
    padding-top: 0px !important;
    padding-bottom: 2rem !important;
    padding-left: 0px !important;
    padding-right: 0px !important;
    margin-top: 0px !important;
    margin-left: 0px !important;
    margin-right: 0px !important;
    max-width: 100% !important;
    width: 100% !important;
}

@media (min-width: 576px) {
    .stApp,
    [data-testid="stAppViewContainer"],
    section.main,
    .stMain,
    div[data-testid="stMain"],
    div[data-testid="stMainBlockContainer"],
    .stMainBlockContainer,
    .block-container {
        padding-left: 0px !important;
        padding-right: 0px !important;
        padding-top: 0px !important;
        max-width: 100% !important;
        width: 100% !important;
    }
}

/* Margen lateral para el contenido de la aplicación debajo del topbar */
div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:not(:has(.topbar-brand)):not(:has(style)):not(:has(.app-topbar-marker)),
div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stLayoutWrapper"]:not(:has(.topbar-brand)) {
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    box-sizing: border-box !important;
}

/* Ocultar elementos contenedores de estilo/marcadores para que no generen gap o margen */
div[data-testid="stElementContainer"]:has(style),
div[data-testid="stElementContainer"]:has(.app-topbar-marker),
div[data-testid="stElementContainer"]:has(.header-banner-marker),
div.element-container:has(style),
div.element-container:has(.app-topbar-marker),
div.element-container:has(.header-banner-marker) {
    display: none !important;
    height: 0px !important;
    min-height: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
}

div[data-testid="stLayoutWrapper"]:has(div[data-testid="stHorizontalBlock"]:has(.topbar-brand)) {
    margin: 0px !important;
    padding: 0px !important;
    width: 100% !important;
    max-width: 100% !important;
}

/* Contenedor Topbar de esquina a esquina */
div[data-testid="stHorizontalBlock"]:has(.topbar-brand) {
    background-color: #ffffff !important;
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 0.35rem 1.5rem 0.35rem 1rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-top: -1.25rem !important;
    margin-left: 0px !important;
    margin-right: 0px !important;
    left: 0px !important;
    right: 0px !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
}

div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="stColumn"]:first-of-type,
div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="column"]:first-of-type {
    justify-content: flex-start !important;
    padding-left: 0px !important;
    margin-left: 0px !important;
}

div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="stColumn"]:last-of-type,
div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="column"]:last-of-type {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    padding-right: 0px !important;
    margin-right: 0px !important;
    margin-left: auto !important;
}

div[data-testid="column"]:has(.topbar-user-marker),
div[data-testid="stColumn"]:has(.topbar-user-marker) {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    height: 100% !important;
}

div[data-testid="column"]:has(.topbar-user-marker) > div[data-testid="stVerticalBlock"],
div[data-testid="stColumn"]:has(.topbar-user-marker) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 0px !important;
    width: 100% !important;
    height: 100% !important;
}

div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stElementContainer"]:has(div[data-testid="stPopover"]),
div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stElementContainer"]:has(div[data-testid="stPopover"]) {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    margin: 0 !important;
    padding: 0 !important;
    width: auto !important;
}

div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"],
div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    margin: 0 !important;
    padding: 0 !important;
}

.topbar-brand {
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    user-select: none !important;
    padding-left: 0px !important;
    margin-left: 0px !important;
}

/* Botón de usuario en el topbar - Icono de persona bi-person */
div[data-testid="column"]:has(.topbar-user-marker) button,
div[data-testid="stColumn"]:has(.topbar-user-marker) button {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    border-radius: 50% !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    width: 36px !important;
    height: 36px !important;
    min-height: 36px !important;
    min-width: 36px !important;
    transition: background-color 0.15s ease !important;
}

div[data-testid="column"]:has(.topbar-user-marker) button:hover,
div[data-testid="stColumn"]:has(.topbar-user-marker) button:hover {
    background-color: rgba(0, 0, 0, 0.06) !important;
    border: none !important;
    box-shadow: none !important;
}

/* Ocultar texto del nombre y flecha chevron */
div[data-testid="column"]:has(.topbar-user-marker) button p,
div[data-testid="stColumn"]:has(.topbar-user-marker) button p,
div[data-testid="column"]:has(.topbar-user-marker) button div[aria-hidden="true"],
div[data-testid="column"]:has(.topbar-user-marker) button [data-testid="stIconMaterial"],
div[data-testid="stColumn"]:has(.topbar-user-marker) button div[aria-hidden="true"],
div[data-testid="stColumn"]:has(.topbar-user-marker) button [data-testid="stIconMaterial"] {
    display: none !important;
}

/* Icono de persona bi-person */
div[data-testid="column"]:has(.topbar-user-marker) button::before,
div[data-testid="stColumn"]:has(.topbar-user-marker) button::before {
    content: "\\f4da" !important;
    font-family: 'bootstrap-icons' !important;
    font-style: normal !important;
    font-weight: normal !important;
    font-size: 1.35rem !important;
    color: #334155 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border-radius: 0 !important;
    width: auto !important;
    height: auto !important;
    transition: color 0.15s ease !important;
}

div[data-testid="column"]:has(.topbar-user-marker) button:hover::before,
div[data-testid="stColumn"]:has(.topbar-user-marker) button:hover::before {
    color: #0284c7 !important;
}

/* Banner de Turnos Sábados - recortado con márgenes */
div[data-testid="stElementContainer"]:has(.premium-gradient-banner) {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-top: 0.75rem !important;
    margin-bottom: 0.75rem !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.premium-gradient-banner {
    background: linear-gradient(90deg, #0a2039 0%, #133554 35%, #2a5d78 70%, #4e8b9e 100%) !important;
    border-radius: 12px !important;
    padding: 0.55rem 1.25rem !important;
    display: flex !important;
    align-items: center !important;
    box-sizing: border-box !important;
    box-shadow: 0 4px 14px rgba(10, 32, 57, 0.2) !important;
    width: 100% !important;
    gap: 0.85rem !important;
}
</style>
<div class="app-topbar-marker"></div>
""", unsafe_allow_html=True)

col_top_brand, col_top_user = st.columns([1, 1])

with col_top_brand:
    img_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
    st.markdown(f"""
        <div class="topbar-brand" style="display:flex; align-items:center; gap:0.5rem; user-select:none;">
            <img src="{img_src}" class="topbar-logo" style="height:28px; max-height:30px; width:auto; object-fit:contain; display:block;" alt="Unión para la Salud y la Vida S.A.S.">
            <span class="topbar-brand-divider" style="display:inline-block; width:1px; height:22px; background-color:#cbd5e1; margin:0 0.85rem;"></span>
            <div class="topbar-titles"><span class="topbar-title" style="font-family:'Outfit', sans-serif; font-size:1.15rem; font-weight:700; color:#0f172a; white-space:nowrap; letter-spacing:-0.2px;">Conexión operativa</span></div>
        </div>
    """, unsafe_allow_html=True)

with col_top_user:
    st.markdown("<div class='topbar-user-marker'></div>", unsafe_allow_html=True)
    with st.popover("", help="Perfil de Usuario • Administración"):
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.5rem;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background-color: #e7f6f4; color: #0d9488; display: flex; align-items: center; justify-content: center; font-size: 1.15rem;">
                    <i class="bi bi-person"></i>
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0f172a; line-height: 1.2;">Juan Jose  Osorio Molina</div>
                    <div style="font-size: 0.78rem; color: #64748b;">Conexión operativa • Administración</div>
                </div>
            </div>
            <div style="margin: 0.5rem 0 0.8rem 0; border-top: 1px solid #e2e8f0;"></div>
        """, unsafe_allow_html=True)
        
        if st.session_state.is_admin:
            st.success("Sesión Iniciada (Admin)", icon=":material/verified_user:")
            if st.button("Cerrar Sesión", use_container_width=True, key="btn_popover_logout"):
                st.session_state.is_admin = False
                if 'saturday_offset' in st.session_state:
                    del st.session_state.saturday_offset
                st.rerun()

            st.markdown("<div style='margin-top:0.8rem; margin-bottom:0.8rem; border-top:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Sincronizar con SharePoint", use_container_width=True, key="btn_sync_direct_sp"):
                st.session_state["force_refresh_personal"] = True
                c_dir = os.path.join(os.path.dirname(__file__), ".cache")
                if os.path.exists(c_dir):
                    for f_name in os.listdir(c_dir):
                        try:
                            os.remove(os.path.join(c_dir, f_name))
                        except Exception:
                            pass
                dp._open_consolidado_conexion.clear()
                dp._get_base_shifts_df.clear()
                dp._open_consolidado_personal.clear()
                dp.load_supernumeraries.clear()
                dp.load_modifications.clear()
                st.cache_data.clear()
                st.cache_resource.clear()
                load_app_data(reload_personal=True)
                st.success("Datos resincronizados directamente con SharePoint.", icon=":material/check_circle:")
                st.rerun()

            with st.expander("🛠️ Purgar Modificaciones en SharePoint", expanded=False):
                st.markdown("Vaciar las modificaciones acumuladas en la Lista de SharePoint (`MODIFICACIONES_SABADOS`).")
                if gc.is_sharepoint_configured():
                    try:
                        current_items = gc.get_sharepoint_list_items("modificaciones_sabados")
                        total_items = len(current_items)
                    except Exception:
                        current_items = []
                        total_items = 0

                    st.info(f"Modificaciones acumuladas: **{total_items}**")
                    if total_items > 0:
                        import json
                        json_bytes = json.dumps(current_items, ensure_ascii=False, indent=2).encode('utf-8')
                        timestamp_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar Respaldo JSON",
                            data=json_bytes,
                            file_name=f"sharepoint_modificaciones_backup_{timestamp_now}.json",
                            mime="application/json",
                            use_container_width=True
                        )

                    confirm_purge = st.checkbox("Confirmar purga completa", key="chk_confirm_purge_popover")
                    if st.button("🧹 Purgar y Reiniciar", type="primary", disabled=(not confirm_purge or total_items == 0), use_container_width=True, key="btn_do_purge_popover"):
                        with st.spinner("Purgando en SharePoint..."):
                            item_ids = [str(it.get("_item_id", it.get("id"))) for it in current_items if it.get("_item_id", it.get("id"))]
                            deleted_count = 0
                            if item_ids:
                                deleted_count = gc.delete_sharepoint_list_items_batch("modificaciones_sabados", item_ids)

                            c_dir = os.path.join(os.path.dirname(__file__), ".cache")
                            if os.path.exists(c_dir):
                                for f_name in os.listdir(c_dir):
                                    try:
                                        os.remove(os.path.join(c_dir, f_name))
                                    except Exception:
                                        pass

                            dp._open_consolidado_conexion.clear()
                            dp._get_base_shifts_df.clear()
                            dp._open_consolidado_personal.clear()
                            dp.load_supernumeraries.clear()
                            dp.load_modifications.clear()
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            load_app_data(reload_personal=True)
                            st.success(f"{deleted_count} modificaciones eliminadas de SharePoint.", icon=":material/check_circle:")
                            st.rerun()
                else:
                    st.warning("SharePoint no configurado.")
        else:
            admin_password = "C3ntr4l1234.*"
            try:
                if "admin_password" in st.secrets:
                    admin_password = st.secrets["admin_password"]
                elif "azure" in st.secrets and "admin_password" in st.secrets["azure"]:
                    admin_password = st.secrets["azure"]["admin_password"]
            except Exception:
                pass

            if 'pwd_error' not in st.session_state:
                st.session_state.pwd_error = None

            def on_pwd_enter():
                val = st.session_state.admin_pwd_popover
                if val == admin_password:
                    st.session_state.is_admin = True
                    if 'saturday_offset' in st.session_state:
                        del st.session_state.saturday_offset
                    st.session_state.pwd_error = None
                else:
                    st.session_state.pwd_error = "Contraseña incorrecta"
                    st.session_state.admin_pwd_popover = ""

            pwd_input = st.text_input(
                "Contraseña de Admin:", 
                type="password", 
                key="admin_pwd_popover", 
                on_change=on_pwd_enter
            )
            
            st.button(
                "Iniciar Sesión", 
                use_container_width=True, 
                key="btn_popover_login",
                on_click=on_pwd_enter
            )
                    
            if st.session_state.pwd_error:
                st.error(st.session_state.pwd_error)

# Banner institucional degradado con título Turnos Sábados
st.markdown("""
    <div class="premium-gradient-banner">
        <div class="premium-banner-icon">
            <i class="bi bi-calendar3"></i>
        </div>
        <div class="premium-banner-text">
            <h1>Turnos Sábados</h1>
            <p>Secuencia sabados</p>
        </div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.data_loaded or st.session_state.load_error:
    st.error(f"### Error al cargar datos")
    st.info(f"Detalle: {st.session_state.load_error}")
    st.stop()

df_shifts = st.session_state.shifts_df
df_super = st.session_state.super_df
# Contenedor principal directo: solo Calendario de Turnos
tab_calendar = st.container()

# Unification layout: click-to-edit instead of sortables

with tab_calendar:
    if not st.session_state.is_admin:
        st.markdown("""
        <div class="info-notice-card">
            Cualquier solicitud de cambio de turno o cambio de secuencia, favor enviar correo a 
            <a href="mailto:central@unionsaludvida.com">central@unionsaludvida.com</a>. 
            Una vez sea aceptado por el correo, se verá reflejado en este cuadro.
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.is_admin and st.session_state.last_action is not None:
        if st.button("Deshacer Último Movimiento", type="secondary", use_container_width=False, icon=":material/undo:"):
            la = st.session_state.last_action
            try:
                if la['action'] in ['ELIMINAR', 'ELIMINAR_SIMPLE']:
                    dp.add_shift_to_date(la['excel_path'], la['sheet'], la['date'], la['doc'], la.get('obs', ''), la.get('clasificacion', 'Secuencia Normal'))
                    st.success("Acción revertida: Médico re-agregado.")
                elif la['action'] == 'ELIMINAR_LOTE':
                    shifts_to_restore = []
                    for item in la.get('deleted_items', []):
                        shifts_to_restore.append({
                            'sheet': item['sheet'],
                            'date': item['date'],
                            'doc': item['doc'],
                            'obs': item['obs'],
                            'clasificacion': item['clasificacion']
                        })
                    dp.add_shifts_batch(la['excel_path'], shifts_to_restore)
                    st.success(f"Acción revertida: {len(la.get('deleted_items', []))} asignaciones de turnos restauradas.")
                elif la['action'] == 'AGREGAR':
                    # Need to delete it. We know date and doc.
                    dp.delete_shift_cell(la['excel_path'], la['sheet'], 0, 0, la['date'], "", la['doc'], la.get('clasificacion', 'Secuencia Normal'))
                    st.success("Acción revertida: Médico eliminado del día.")
                elif la['action'] == 'MOVE':
                    # Delete from new_date, add to old_date
                    dp.delete_shift_cell(la['excel_path'], la['sheet'], 0, 0, la['new_date'], "", la['doc'], la.get('clasificacion', 'Secuencia Normal'))
                    dp.add_shift_to_date(la['excel_path'], la['sheet'], la['old_date'], la['doc'], la.get('obs', ''), la.get('clasificacion', 'Secuencia Normal'))
                    st.success("Acción revertida: Movimiento cancelado.")
                elif la['action'] == 'REPLACE':
                    dp.update_shift_cell(
                        excel_path=la['excel_path'],
                        sheet_name=la['sheet'],
                        row_idx=la['row'],
                        col_idx=la['col'],
                        new_name=la['old_doc'],
                        date_val=la['date'],
                        observation=la['old_obs'],
                        original_name=la['new_doc'],
                        clasificacion=la['old_clasif']
                    )
                    st.success("Acción revertida: Reemplazo / edición cancelado.")
                
                st.session_state.last_action = None
                load_app_data()
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo deshacer: {e}")

    if "search_input" not in st.session_state:
        st.session_state["search_input"] = ""

    if st.session_state.get("clear_search_flag", False):
        st.session_state["search_input"] = ""
        st.session_state["clear_search_flag"] = False

    def clear_search():
        st.session_state["search_input"] = ""

    def refresh_data():
        st.cache_data.clear()
        st.cache_resource.clear()
        # load_app_data() happens on rerun

    col_spacer1, col_lbl, col_search, col_btn_search, col_btn_clear, col_refresh, col_spacer2 = st.columns([1.2, 0.5, 2.2, 0.3, 0.3, 0.3, 1.2])
    with col_lbl:
        st.markdown("<div class='search-label'>Buscar:</div>", unsafe_allow_html=True)
    with col_search:
        search_query = st.text_input("Buscador", key="search_input", placeholder="", label_visibility="collapsed").strip().upper()
    
    with col_btn_search:
        st.markdown("<div class='search-btn-marker'></div>", unsafe_allow_html=True)
        st.button("B", key="btn_search", use_container_width=True)
    with col_btn_clear:
        st.markdown("<div class='clear-btn-marker'></div>", unsafe_allow_html=True)
        st.button("L", key="btn_clear", use_container_width=True, on_click=clear_search)
    with col_refresh:
        st.markdown("<div class='refresh-btn-marker'></div>", unsafe_allow_html=True)
        st.button("R", key="btn_refresh", help="Recargar datos", use_container_width=True, on_click=refresh_data)

    # Inicializar estado para el filtro de clasificación si no existe
    if "filter_class" not in st.session_state:
        st.session_state["filter_class"] = "Todos"

    if not st.session_state.is_admin:
        # Fila de píldoras/botones de filtro dinámico
        st.markdown("<div style='margin-top: 0.15rem;'></div>", unsafe_allow_html=True)
        col_spacer_l, col_lbl_f, col_btn_f1, col_btn_f2, col_btn_f3, col_spacer_r = st.columns([2.2, 1.2, 1.8, 1.8, 2.2, 2.2])
        with col_lbl_f:
            st.markdown("<div style='font-size: 0.95rem; color: #555; font-weight: bold; padding-top: 0.35rem; text-align: right; font-family: Outfit;'>Filtrar por:</div>", unsafe_allow_html=True)
        with col_btn_f1:
            st.markdown("<div class='filter-all-marker'></div>", unsafe_allow_html=True)
            f_style_all = "primary" if st.session_state["filter_class"] == "Todos" else "secondary"
            if st.button("Todos", key="btn_filter_all", use_container_width=True, type=f_style_all):
                st.session_state["filter_class"] = "Todos"
                st.rerun()
        with col_btn_f2:
            st.markdown("<div class='filter-normal-marker'></div>", unsafe_allow_html=True)
            f_style_normal = "primary" if st.session_state["filter_class"] == "Secuencia Normal" else "secondary"
            if st.button("Normal", key="btn_filter_normal", use_container_width=True, type=f_style_normal):
                st.session_state["filter_class"] = "Secuencia Normal"
                st.rerun()
        with col_btn_f3:
            st.markdown("<div class='filter-comp-marker'></div>", unsafe_allow_html=True)
            f_style_comp = "primary" if st.session_state["filter_class"] == "Compensación" else "secondary"
            if st.button("Compensación", key="btn_filter_comp", use_container_width=True, type=f_style_comp):
                st.session_state["filter_class"] = "Compensación"
                st.rerun()
    else:
        st.session_state["filter_class"] = "Todos"

    st.components.v1.html(r"""
    <script>
    function styleButtons() {
        // Estilizar botones de médico y encabezados en modo Administrador/Público (en la grilla de columnas)
        const colButtons = window.parent.document.querySelectorAll('div[data-testid="stColumn"]:has(.saturday-col-marker) button');
        colButtons.forEach(btn => {
            const text = (btn.innerText || "").trim();
            if (!text) return;
            // Ignorar el botón del engranaje (Popover Admin) para que no se sobreescriba
            if (text.includes('⚙️')) return;
            
            // 2a. Si empieza con un número, es el botón del ENCABEZADO de la fecha
            if (/^\d/.test(text)) {
                btn.classList.add('custom-header-btn');
                btn.style.setProperty('background', 'linear-gradient(180deg, #1b8dfd 0%, #0866ea 100%)', 'important');
                btn.style.setProperty('background-color', '#0866ea', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('box-shadow', '0 4px 14px rgba(8, 102, 234, 0.35)', 'important');
                btn.style.setProperty('font-weight', '700', 'important');
                btn.style.setProperty('font-size', '0.92rem', 'important');
                btn.style.setProperty('border-radius', '12px', 'important');
                btn.style.setProperty('width', '100%', 'important');
                btn.style.setProperty('display', 'block', 'important');
                btn.style.setProperty('margin-bottom', '0.35rem', 'important');
                btn.style.setProperty('padding', '0.45rem 0.6rem', 'important');
                btn.style.setProperty('text-shadow', '0 1px 2px rgba(0, 0, 0, 0.15)', 'important');
                const pHeader = btn.querySelector('p, span');
                if (pHeader) {
                    pHeader.style.setProperty('color', '#ffffff', 'important');
                    pHeader.style.setProperty('font-weight', '700', 'important');
                }
                return;
            }

            // Estilizar botón Agregar Médico con rgb(20, 116, 220)
            if (text.includes("Agregar Médico")) {
                btn.style.setProperty('background-color', 'rgb(20, 116, 220)', 'important');
                btn.style.setProperty('background', 'rgb(20, 116, 220)', 'important');
                btn.style.setProperty('border-color', 'rgb(20, 116, 220)', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.querySelectorAll('*').forEach(el => el.style.setProperty('color', '#ffffff', 'important'));
                return;
            }

            // Ignorar Duplicar
            if (text.includes("Duplicar")) {
                return;
            }

            let bg = '#ffffff'; // Blanco limpio
            let fg = '#262730'; // Texto oscuro nítido
            let border = 'rgba(49, 51, 63, 0.2)';
            let shadow = '0 1px 2px rgba(0, 0, 0, 0.04)';

            if (text.includes('🎯')) {
                bg = '#fff8e1';
                fg = '#e65100';
                border = '#ffc107';
                shadow = '0 0 12px rgba(255, 193, 7, 0.4)';
            } else if (text.includes('DUPLICADO') || text.includes('🚨')) {
                bg = '#ffebee';
                fg = '#c62828';
                border = '#ffcdd2';
            } else if (text.includes('COMP') || text.includes('🟡')) {
                bg = '#fffde6';
                fg = '#b58900';
                border = '#ffecb3';
            } else if (text.includes('Cambio') || text.includes('🔄')) {
                bg = '#e8f5e9'; // verde/teal suave
                fg = '#2e7d32';
                border = '#c8e6c9';
            }

            btn.style.setProperty('background', bg, 'important');
            btn.style.setProperty('background-color', bg, 'important');
            btn.style.setProperty('color', fg, 'important');
            btn.style.setProperty('border-color', border, 'important');
            btn.style.setProperty('box-shadow', shadow, 'important');
            btn.style.setProperty('border-style', 'solid', 'important');
            btn.style.setProperty('border-width', '1px', 'important');
            btn.style.setProperty('border-radius', '8px', 'important');
            btn.style.setProperty('font-weight', '500', 'important');
            btn.style.setProperty('font-size', '0.8rem', 'important');
            btn.style.setProperty('padding', '0.22rem 0.5rem', 'important');
            btn.style.setProperty('width', '100%', 'important');
            btn.style.setProperty('display', 'block', 'important');
            btn.style.setProperty('margin-bottom', '0px', 'important');
            btn.style.setProperty('min-height', 'auto', 'important');
            btn.style.setProperty('line-height', '1.15', 'important');
            btn.style.setProperty('text-shadow', 'none', 'important');

            const childs = btn.querySelectorAll('*');
            childs.forEach(c => {
                c.style.setProperty('color', fg, 'important');
                c.style.setProperty('background-color', 'transparent', 'important');
                c.style.setProperty('text-shadow', 'none', 'important');
            });
        });
    }
    styleButtons();
    const observer = new MutationObserver(styleButtons);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """, height=0)

    # Renderizar alerta de error en la ventana padre si el flag está activo
    if st.session_state.get("show_error_alert", False):
        alert_id = datetime.datetime.now().timestamp()
        st.components.v1.html(f"""
        <script>
            // Alert ID: {alert_id}
            try {{
                const runAlert = () => {{
                    window.parent.Swal.fire({{
                        title: "Error",
                        text: "El nombre no existe, ingrese un nuevo nombre",
                        icon: "error",
                        draggable: true,
                        confirmButtonColor: '#1a73e8'
                    }});
                }};

                if (!window.parent.Swal) {{
                    const script = window.parent.document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    script.onload = runAlert;
                    window.parent.document.head.appendChild(script);
                }} else {{
                    runAlert();
                }}
            }} catch (e) {{
                console.error("SweetAlert2 parent injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_error_alert"] = False

    # Renderizar alerta de ÉXITO de eliminación desde el nivel principal (no dentro del dialog)
    # Usamos delete_alert_counter como ID único para forzar el re-render en cada eliminación
    if st.session_state.get("show_delete_success_alert", False):
        deleted_doc = st.session_state.get("deleted_doc_name", "Médico")
        alert_counter = st.session_state.get("delete_alert_counter", 0)
        st.components.v1.html(f"""
        <script>
            // Alerta de éxito #{alert_counter} - ID único para forzar re-render
            try {{
                const runSuccessAlert = () => {{
                    window.parent.Swal.fire({{
                        title: "✅ Eliminado",
                        text: "{deleted_doc} fue eliminado correctamente.",
                        icon: "success",
                        draggable: true,
                        confirmButtonColor: '#1a73e8',
                        timer: 1500,
                        timerProgressBar: true
                    }});
                }};
                if (!window.parent.Swal) {{
                    const script = window.parent.document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    script.onload = runSuccessAlert;
                    window.parent.document.head.appendChild(script);
                }} else {{
                    runSuccessAlert();
                }}
            }} catch (e) {{
                console.error("SweetAlert2 success injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_delete_success_alert"] = False

    # Renderizar alerta de ÉXITO de agregar médico desde el nivel principal
    if st.session_state.get("show_add_success_alert", False):
        added_doc = st.session_state.get("added_doc_name", "Médico")
        add_counter = st.session_state.get("add_alert_counter", 0)
        st.components.v1.html(f"""
        <script>
            // Alerta de éxito agregar #{add_counter} - ID único
            try {{
                const runAddSuccessAlert = () => {{
                    window.parent.Swal.fire({{
                        title: "✅ Agregado",
                        text: "{added_doc} fue agregado correctamente.",
                        icon: "success",
                        draggable: true,
                        confirmButtonColor: '#1a73e8',
                        timer: 3500,
                        timerProgressBar: true
                    }});
                }};
                if (!window.parent.Swal) {{
                    const script = window.parent.document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    script.onload = runAddSuccessAlert;
                    window.parent.document.head.appendChild(script);
                }} else {{
                    runAddSuccessAlert();
                }}
            }} catch (e) {{
                console.error("SweetAlert2 add success injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_add_success_alert"] = False

    today = datetime.date.today()
    days_to_sat = (5 - today.weekday()) % 7
    first_sat = today + datetime.timedelta(days=days_to_sat)
    generated_sats = [first_sat + datetime.timedelta(weeks=w) for w in range(52)]
    
    if st.session_state.is_admin:
        db_sats = []
        if not df_shifts.empty and 'Date' in df_shifts.columns:
            db_sats = [d for d in df_shifts['Date'].unique() if isinstance(d, (datetime.date, datetime.datetime))]
            db_sats = [d.date() if isinstance(d, datetime.datetime) else d for d in db_sats]
        all_visible_saturdays = sorted(list(set(db_sats + generated_sats)))
    else:
        db_future_sats = []
        if not df_shifts.empty and 'Date' in df_shifts.columns:
            db_future_sats = [d for d in df_shifts['Date'].unique() if d >= today]
            db_future_sats = [d.date() if isinstance(d, datetime.datetime) else d for d in db_future_sats]
        all_visible_saturdays = sorted(list(set(db_future_sats + generated_sats)))
    
    if not all_visible_saturdays:
        st.info("No se encontraron turnos de sábados programados.")
    else:
        if st.session_state.is_admin:
            # Encontrar el índice del primer sábado futuro (>= today) para inicializar el offset si no existe
            next_sat_idx = 0
            for idx, sat in enumerate(all_visible_saturdays):
                if sat >= today:
                    next_sat_idx = idx
                    break
            
            if 'saturday_offset' not in st.session_state:
                st.session_state.saturday_offset = next_sat_idx
            
            if st.session_state.saturday_offset >= len(all_visible_saturdays):
                st.session_state.saturday_offset = max(0, ((len(all_visible_saturdays) - 1) // 4) * 4)
                
            offset = st.session_state.saturday_offset
            saturdays = all_visible_saturdays[offset:offset+4]
            
            col_nav_prev, col_nav_info, col_nav_next = st.columns([1.2, 2, 1.2])
            with col_nav_prev:
                has_prev = offset > 0
                if st.button("◀ Sábados Anteriores", use_container_width=True, disabled=not has_prev, key="btn_prev_sats"):
                    st.session_state.saturday_offset = max(0, offset - 4)
                    st.rerun()
            with col_nav_info:
                start_sat = offset + 1
                end_sat = min(len(all_visible_saturdays), offset + 4)
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 0.5rem; color: #1565c0; font-family: Outfit; font-size: 1.05rem;'>Sábados {start_sat} a {end_sat} de {len(all_visible_saturdays)} programados</div>", unsafe_allow_html=True)
            with col_nav_next:
                has_next = offset + 4 < len(all_visible_saturdays)
                if st.button("Siguientes Sábados ▶", use_container_width=True, disabled=not has_next, key="btn_next_sats"):
                    st.session_state.saturday_offset = offset + 4
                    st.rerun()
        else:
            saturdays = all_visible_saturdays[:4]
            
        month_shifts = df_shifts[df_shifts['Date'].isin(saturdays)] if not df_shifts.empty else pd.DataFrame()
        
        if search_query:
            search_shifts = month_shifts.copy()
            filter_val = st.session_state.get("filter_class", "Todos")
            if filter_val != "Todos" and not search_shifts.empty and 'Classification' in search_shifts.columns:
                search_shifts = search_shifts[search_shifts['Classification'].str.contains(filter_val, na=False, case=False)]
            
            found = False
            if not search_shifts.empty and search_shifts['Supernumerary'].str.upper().str.contains(search_query, na=False).any():
                found = True
                
            if not found:
                st.session_state["clear_search_flag"] = True
                st.session_state["show_error_alert"] = True
                st.rerun()
        
        if st.session_state.is_admin:
            # ADMIN VIEW: Interactive Grid inside container (Click to edit)
            st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
            st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
            cols = st.columns(len(saturdays))
            for idx, sat_date in enumerate(saturdays):
                with cols[idx]:
                    st.markdown("<div class='saturday-col-marker'></div>", unsafe_allow_html=True)
                    is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                    holiday_class = " holiday" if is_holiday else ""
                    
                    date_shifts_all = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                    num_doctors_all = len(date_shifts_all)
                    doc_counts = date_shifts_all['Supernumerary'].value_counts() if not date_shifts_all.empty else pd.Series()
                    
                    # Initialize column_sorts state if not exists
                    if 'column_sorts' not in st.session_state:
                        st.session_state.column_sorts = {}
                    sort_type = st.session_state.column_sorts.get(sat_date, "natural")

                    header_text = f"{sat_date.day} {dp.MONTH_NAMES_SP[sat_date.month]} {sat_date.year}"
                    header_text += f" ({num_doctors_all} Médicos)"
                    if is_holiday:
                        header_text += " (FESTIVO)"
                    if sort_type == "asc":
                        header_text += " 🔤"
                        
                    st.markdown("<div class='date-header-marker'></div>", unsafe_allow_html=True)
                    if st.button(header_text, key=f"header_sort_admin_{sat_date}", use_container_width=True):
                        st.session_state.column_sorts[sat_date] = "natural" if sort_type == "asc" else "asc"
                        st.rerun()
                    
                    # Render doctor list as clickable buttons
                    date_shifts_loop = date_shifts_all.sort_values(by='Supernumerary') if sort_type == "asc" else date_shifts_all
                    for s_idx, s_row in date_shifts_loop.reset_index().iterrows():
                        name = s_row['Supernumerary']
                        shift_obs = str(s_row.get('Observation', '')) if pd.notna(s_row.get('Observation')) else ''
                        clasif = s_row.get('Classification', 'Secuencia Normal')
                        
                        personal_obs = ""
                        if not df_super.empty:
                            doc_match = df_super[df_super['NOMBRES Y APELLIDOS'] == name]
                            if not doc_match.empty:
                                personal_obs = str(doc_match.iloc[0].get('OBSERVACIONES', '')).strip()
                                
                        has_conflict = doc_counts.get(name, 0) > 1
                        
                        # Prepare display name with suffixes for the admin button
                        display_name = name
                        if has_conflict:
                            display_name += " 🚨(DUPLICADO)"
                        if "Compensación" in str(clasif):
                            display_name += " 🟡(COMP)"
                        elif "Cambio" in str(clasif):
                            display_name += f" 🔄({clasif.split(' con ')[0]})"  # extract just prefix
                            
                        if search_query and search_query in name.upper():
                            display_name = "🎯 " + display_name
                            
                        if shift_obs or personal_obs:
                            display_name += " 💬"
                            
                        # Help tooltip
                        has_obs = (clasif and clasif != "Secuencia Normal") or shift_obs or personal_obs
                        help_lines = []
                        if "Compensación" in str(clasif): help_lines.append("⚠️ Turno de compensación")
                        if clasif and clasif != "Secuencia Normal": help_lines.append(f"ℹ️ {clasif}")
                        if shift_obs: help_lines.append(f"💬 {shift_obs}")
                        if personal_obs: help_lines.append(f"👤 {personal_obs}")
                        
                        help_text = "\n".join(help_lines).strip()
                        
                        # Clickable button styled as badge
                        if st.button(display_name, key=f"edit_btn_{sat_date}_{name}_{s_idx}", use_container_width=True, help=help_text if help_text else None):
                            action_details = {
                                'date': sat_date,
                                'doctor': name,
                                'row': int(s_row['Excel_Row']),
                                'col': int(s_row['Excel_Col']),
                                'sheet': s_row['Sheet'],
                                'observation': shift_obs,
                                'classification': clasif
                            }
                            ui_dialogs.show_shift_dialog(action_details, load_app_data)
                        
                    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
                    
                    # 1. Agregar Médico button
                    sheet_name = date_shifts_all.iloc[0]['Sheet'] if not date_shifts_all.empty else f"SABADOS {sat_date.year}"
                    if st.button("Agregar Médico", key=f"add_btn_col_{sat_date}", use_container_width=True, type="primary", icon=":material/person_add:"):
                        ui_dialogs.show_add_dialog(sat_date, sheet_name, load_app_data)
                        
                    # 2. Duplicar button (if prev shifts exist)
                    two_weeks_ago = sat_date - datetime.timedelta(weeks=2)
                    prev_shifts = df_shifts[df_shifts['Date'] == two_weeks_ago] if not df_shifts.empty else pd.DataFrame()
                    if not prev_shifts.empty:
                        st.markdown("<div class='dup-btn-wrapper'></div>", unsafe_allow_html=True)
                        label_dup = f"Duplicar del {two_weeks_ago.day} {dp.MONTH_NAMES_SP[two_weeks_ago.month]}"
                        if st.button(label_dup, key=f"dup_btn_col_{sat_date}", use_container_width=True):
                            with st.spinner("Duplicando..."):
                                try:
                                    target_sheet = date_shifts_all.iloc[0]['Sheet'] if not date_shifts_all.empty else f"SABADOS {sat_date.year}"
                                    
                                    shifts_to_delete_list = []
                                    if not date_shifts_all.empty:
                                        for _, row_to_del in date_shifts_all.iterrows():
                                            clasif_dest = str(row_to_del.get('Classification', 'Secuencia Normal'))
                                            if "Compensación" in clasif_dest or "Cambio" in clasif_dest:
                                                continue  # Keep compensation or swap shifts
                                            shifts_to_delete_list.append({
                                                'sheet': row_to_del['Sheet'],
                                                'doctor': row_to_del['Supernumerary'],
                                                'row': int(row_to_del['Excel_Row']),
                                                'col': int(row_to_del['Excel_Col'])
                                            })
                                            
                                    shifts_to_add_list = []
                                    for _, row_to_copy in prev_shifts.iterrows():
                                        clasif_orig = str(row_to_copy.get('Classification', 'Secuencia Normal'))
                                        if "Compensación" in clasif_orig or "Cambio" in clasif_orig:
                                            continue  # Skip source compensations or swaps
                                        shifts_to_add_list.append({
                                            'doctor': row_to_copy['Supernumerary'],
                                            'observation': row_to_copy.get('Observation', ''),
                                            'classification': row_to_copy.get('Classification', 'Secuencia Normal')
                                        })
                                        
                                    dp.duplicate_schedule_batch(
                                        excel_path=st.session_state.excel_path,
                                        target_sheet=target_sheet,
                                        target_date=sat_date,
                                        shifts_to_delete_list=shifts_to_delete_list,
                                        shifts_to_add_list=shifts_to_add_list
                                    )
                                    st.success(f"Programación duplicada del {two_weeks_ago.day} de {dp.MONTH_NAMES_SP[two_weeks_ago.month]}")
                                    load_app_data()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error al duplicar: {e}")
                                    
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            # PUBLIC VIEW: Read-Only Grid inside container
            with st.container():
                st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
                st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
                cols = st.columns(len(saturdays))
                for idx, sat_date in enumerate(saturdays):
                    with cols[idx]:
                        st.markdown("<div class='saturday-col-marker'></div>", unsafe_allow_html=True)
                        is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                        holiday_class = " holiday" if is_holiday else ""
                        
                        date_shifts_all = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                        num_doctors_all = len(date_shifts_all)
                        
                        # Aplicar filtro de clasificación
                        date_shifts = date_shifts_all.copy()
                        filter_val = st.session_state.get("filter_class", "Todos")
                        if filter_val != "Todos":
                            date_shifts = date_shifts[date_shifts['Classification'].str.contains(filter_val, na=False, case=False)]
                        
                        num_doctors_filtered = len(date_shifts)
                        
                        # Initialize column_sorts state if not exists
                        if 'column_sorts' not in st.session_state:
                            st.session_state.column_sorts = {}
                        sort_type = st.session_state.column_sorts.get(sat_date, "natural")

                        header_text = f"{sat_date.day} {dp.MONTH_NAMES_SP[sat_date.month]} {sat_date.year}"
                        if filter_val != "Todos":
                            header_text += f" ({num_doctors_filtered}/{num_doctors_all} Médicos)"
                        else:
                            header_text += f" ({num_doctors_all} Médicos)"
                        if is_holiday:
                            header_text += " (FESTIVO)"
                        if sort_type == "asc":
                            header_text += " 🔤"
                            
                        st.markdown("<div class='date-header-marker'></div>", unsafe_allow_html=True)
                        if st.button(header_text, key=f"header_sort_pub_{sat_date}", use_container_width=True):
                            st.session_state.column_sorts[sat_date] = "natural" if sort_type == "asc" else "asc"
                            st.rerun()
                        
                        date_shifts_loop = date_shifts.sort_values(by='Supernumerary') if sort_type == "asc" else date_shifts
                        for _, s_row in date_shifts_loop.reset_index().iterrows():
                            name = s_row['Supernumerary']
                            shift_obs = str(s_row.get('Observation', '')) if pd.notna(s_row.get('Observation')) else ''
                            clasif = s_row.get('Classification', 'Secuencia Normal')
                            is_compensation = "Compensación" in str(clasif)
                            
                            personal_obs = ""
                            if not df_super.empty:
                                doc_match = df_super[df_super['NOMBRES Y APELLIDOS'] == name]
                                if not doc_match.empty:
                                    personal_obs = str(doc_match.iloc[0].get('OBSERVACIONES', '')).strip()
                                    
                            has_obs = (clasif and clasif != "Secuencia Normal") or shift_obs or personal_obs
                            help_lines = []
                            if is_compensation: help_lines.append("⚠️ Turno de compensación")
                            if clasif and clasif != "Secuencia Normal": help_lines.append(f"ℹ️ {clasif}")
                            if shift_obs: help_lines.append(f"💬 {shift_obs}")
                            if personal_obs: help_lines.append(f"👤 {personal_obs}")
                            
                            help_text = "<br>".join(help_lines).strip()
                            badge_classes = "doc-name-badge" + (" has-obs" if has_obs else "")
                            if search_query and search_query in name.upper():
                                badge_classes += " search-highlight"
                                
                            obs_dot = "<span class='obs-dot'></span>" if has_obs else ""
                            tooltip_html = f"<div class='doc-obs-tooltip'>{help_text}</div>" if help_text else ""
                            
                            # Add suffix to public view name if swap/change is active
                            display_name = name
                            if "Cambio" in str(clasif):
                                display_name += f" ({clasif})"
                            
                            st.markdown(f"<div class='doc-btn-wrap'><div class='{badge_classes}'>{obs_dot}{display_name}</div>{tooltip_html}</div>", unsafe_allow_html=True)
                            
                st.markdown("</div>", unsafe_allow_html=True)


# Footer
st.markdown(
    """
    <div class='app-footer'>
        © 2026 - Unión para la Salud y la Vida
    </div>
    """, 
    unsafe_allow_html=True
)

st.components.v1.html(
    """
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
            
            // Ocultar el botón flotante de "Gestionar la aplicación" de Streamlit Cloud
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
    """,
    height=0,
    width=0
)