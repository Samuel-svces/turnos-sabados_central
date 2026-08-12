# pyrefly: ignore [missing-import]
# Actualización forzada del layout
import streamlit as st
import pandas as pd
import datetime
import os
import re
import data_processor as dp
import styles
import ui_dialogs

# Set page config for Streamlit
st.set_page_config(
    page_title="TURNOS SABADOS DE LOS SUPERNUMERARIOS",
    page_icon="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/icons/calendar3.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
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
                    [data-testid="stAppDeployButton"] {
                        display: none !important;
                        visibility: hidden !important;
                        opacity: 0 !important;
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
    if platform.system() == "Windows":
        # Ejecución local en Windows: buscar el maestro en rutas conocidas
        default_paths = [
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
        # Ejecución en Streamlit Cloud: se usan credenciales Azure via graph_client
        st.session_state.excel_path = "TURNOS SABADOS.xlsx"  # placeholder (no se accede a disco)

# Function to load and clean data
def load_app_data():
    try:
        # Load Saturday shifts
        df_shifts, errors = dp.load_data(st.session_state.excel_path)
        st.session_state.shifts_df = df_shifts
        st.session_state.errors = errors
        
        # Load Supernumeraries directory
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

st.markdown("<div class='header-banner-marker'></div>", unsafe_allow_html=True)

col_gear, col_spacer, col_empty = st.columns([1, 10, 1])
with col_gear:
    st.markdown("<div class='admin-gear-marker'></div>", unsafe_allow_html=True)
    with st.popover("⚙️", help="Administración"):
        st.markdown("#### <i class='bi bi-shield-lock-fill'></i> Acceso Administrador", unsafe_allow_html=True)
        
        if st.session_state.is_admin:
            st.success("Sesión Iniciada (Admin)")
            if st.button("Cerrar Sesión", use_container_width=True, key="btn_popover_logout"):
                st.session_state.is_admin = False
                if 'saturday_offset' in st.session_state:
                    del st.session_state.saturday_offset
                st.rerun()
        else:
            admin_password = "C3ntr4l1234.*"
            try:
                if "admin_password" in st.secrets:
                    admin_password = st.secrets["admin_password"]
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

with col_spacer:
    st.markdown("""
        <div class="premium-banner-transparent">
            <div class="premium-banner-text">
                <h1>Turnos Sabados</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)

if not st.session_state.data_loaded or st.session_state.load_error:
    st.error(f"### Error al cargar datos")
    st.info(f"Detalle: {st.session_state.load_error}")
    st.stop()

df_shifts = st.session_state.shifts_df
df_super = st.session_state.super_df
# Navigation Tabs
# Navigation Tabs
if st.session_state.is_admin:
    tabs = st.tabs(["Calendario de Turnos", "Directorio y Sincronización"])
    tab_calendar = tabs[0]
    tab_admin = tabs[1]
else:
    tab_calendar = st.container()

# Unification layout: click-to-edit instead of sortables

with tab_calendar:
    if not st.session_state.is_admin:
        st.markdown("""
        <div style="background-color:#e8f4fd; border-radius:8px; padding:12px; text-align:center;">
            Cualquier solicitud de cambio de turno o cambio de secuencia, favor enviar correo a 
            <a href="mailto:central@sanvicenteces.com"><strong>central@sanvicenteces.com</strong></a>. 
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
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
        col_spacer_l, col_lbl_f, col_btn_f1, col_btn_f2, col_btn_f3, col_spacer_r = st.columns([2.2, 1.2, 1.8, 1.8, 2.2, 2.2])
        with col_lbl_f:
            st.markdown("<div style='font-size: 0.95rem; color: #555; font-weight: bold; padding-top: 0.35rem; text-align: right; font-family: Outfit;'>Filtrar por:</div>", unsafe_allow_html=True)
        with col_btn_f1:
            st.markdown("<div class='filter-all-marker'></div>", unsafe_allow_html=True)
            f_style_all = "primary" if st.session_state["filter_class"] == "Todos" else "secondary"
            if st.button("🔵 Todos", key="btn_filter_all", use_container_width=True, type=f_style_all):
                st.session_state["filter_class"] = "Todos"
                st.rerun()
        with col_btn_f2:
            st.markdown("<div class='filter-normal-marker'></div>", unsafe_allow_html=True)
            f_style_normal = "primary" if st.session_state["filter_class"] == "Secuencia Normal" else "secondary"
            if st.button("🟢 Normal", key="btn_filter_normal", use_container_width=True, type=f_style_normal):
                st.session_state["filter_class"] = "Secuencia Normal"
                st.rerun()
        with col_btn_f3:
            st.markdown("<div class='filter-comp-marker'></div>", unsafe_allow_html=True)
            f_style_comp = "primary" if st.session_state["filter_class"] == "Compensación" else "secondary"
            if st.button("🟡 Compensación", key="btn_filter_comp", use_container_width=True, type=f_style_comp):
                st.session_state["filter_class"] = "Compensación"
                st.rerun()
    else:
        st.session_state["filter_class"] = "Todos"

    st.components.v1.html("""
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
                btn.style.setProperty('background-color', '#005eb8', 'important');
                btn.style.setProperty('color', 'white', 'important');
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('box-shadow', '0 4px 10px rgba(0,94,184,0.15)', 'important');
                btn.style.setProperty('font-weight', '700', 'important');
                btn.style.setProperty('font-size', '0.92rem', 'important');
                btn.style.setProperty('border-radius', '8px', 'important');
                btn.style.setProperty('width', '100%', 'important');
                btn.style.setProperty('display', 'block', 'important');
                btn.style.setProperty('margin-bottom', '0.75rem', 'important');
                btn.style.setProperty('padding', '0.55rem 0.6rem', 'important');
                const pHeader = btn.querySelector('p, span');
                if (pHeader) {
                    pHeader.style.setProperty('color', 'white', 'important');
                    pHeader.style.setProperty('font-weight', '700', 'important');
                }
                return;
            }

            // Ignorar los botones de control de columna (Agregar / Duplicar)
            if (text.includes("Agregar Médico") || text.includes("Duplicar")) {
                return;
            }

            let bg = '#fbf6eb'; // crema premium
            let fg = '#5c4d3c'; // marrón oscuro elegante
            let border = '#e6dec9';
            let shadow = '0 1px 3px rgba(0,0,0,0.05)';

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

            const childs = btn.querySelectorAll('*');
            childs.forEach(c => {
                c.style.setProperty('color', fg, 'important');
                c.style.setProperty('background-color', 'transparent', 'important');
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
                        timer: 3500,
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


# ----------------- TAB 3: ADMIN CONTROL PANEL -----------------
if st.session_state.is_admin:
    with tab_admin:
        st.markdown("### <i class='bi bi-sliders2'></i> Directorio de Personal y Sincronización", unsafe_allow_html=True)
        st.markdown("Gestión de altas, bajas y modificaciones en el directorio de médicos supernumerarios, y sincronización con el repositorio Excel.")
        
        col_dir, col_hist = st.columns([1.1, 0.9])
        
        with col_dir:
            st.markdown("#### <i class='bi bi-cloud-check'></i> Directorio de Personal en SharePoint", unsafe_allow_html=True)
            st.info("El directorio se sincroniza automáticamente desde el archivo de SharePoint **CONSOLIDADO 2026.xlsx** (hoja **BD PERSONAL**). Se muestran los médicos con Sede **Supernumerario** o **Induccion**.")
            
            num_super = len(df_super) if not df_super.empty else 0
            col_m1, col_m2 = st.columns([1, 1])
            with col_m1:
                st.metric("Médicos Supernumerarios Activos", f"{num_super} Médicos")
            with col_m2:
                if st.button("🔄 Sincronizar desde SharePoint", use_container_width=True):
                    st.session_state["force_refresh_personal"] = True
                    for c_file in ["CONSOLIDADO_2026_cached.xlsx", "CONSOLIDADO_2026_cached_meta.txt"]:
                        if os.path.exists(c_file):
                            try:
                                os.remove(c_file)
                            except Exception:
                                pass
                    dp._open_consolidado_personal.clear()
                    dp.load_supernumeraries.clear()
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    load_app_data()
                    st.success("Directorio de personal resincronizado con éxito desde SharePoint.")
                    st.rerun()
            
            st.markdown("##### 📋 Listado Activo de Supernumerarios")
            if not df_super.empty:
                search_super = st.text_input("🔍 Buscar médico por nombre o cédula:", placeholder="Escriba un nombre o cédula...").strip().upper()
                df_show = df_super.copy()
                if search_super:
                    mask_name = df_show['NOMBRES Y APELLIDOS'].str.contains(search_super, na=False)
                    mask_ced  = df_show['CEDULA'].astype(str).str.contains(search_super, na=False)
                    df_show = df_show[mask_name | mask_ced]
                
                st.dataframe(
                    df_show[['CEDULA', 'NOMBRES Y APELLIDOS', 'CARGO', 'SEDE / CECO', 'CELULAR', 'OBSERVACIONES']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No se encontraron médicos activos con Sede 'Supernumerario' o 'Induccion' en la hoja BD PERSONAL de SharePoint.")
                if st.session_state.get('super_load_error'):
                    st.error(f"Detalle del error de conexión: {st.session_state.super_load_error}")
            
            st.markdown("---")
            st.markdown("#### ⚠️ Plan de Contingencia: Registro Manual de Médicos", unsafe_allow_html=True)
            st.caption("Si un médico no ha sido ingresado a tiempo en la BD PERSONAL de SharePoint, puedes registrarlo temporalmente aquí para que aparezca en el sistema.")
            
            with st.expander("➕ Registrar Médico Manualmente (Contingencia)", expanded=False):
                with st.form("admin_manual_doc_form", clear_on_submit=True):
                    m_cedula = st.text_input("Cédula / Identificación:").strip()
                    m_nombre = st.text_input("Nombre Completo (APELLIDOS NOMBRES):").strip().upper()
                    m_sede = st.selectbox("Sede / CECO:", ["SUPERNUMERARIOS", "INDUCCION"])
                    m_celular = st.text_input("Celular (opcional):").strip()
                    m_obs = st.text_area("Observaciones de Contingencia:", placeholder="Ej: Registro urgente por turno sábado...", height=70).strip()
                    
                    sub_manual = st.form_submit_button("Registrar Médico en Contingencia", use_container_width=True)
                    if sub_manual:
                        if not m_cedula or not m_nombre:
                            st.error("Cédula y Nombre Completo son obligatorios.")
                        else:
                            doc_data = {
                                'cedula': m_cedula,
                                'nombres_y_apellidos': m_nombre,
                                'cargo': 'MEDICO GENERAL SUPERNUMERARIO',
                                'celular': m_celular,
                                'sede_ceco': m_sede,
                                'observaciones': m_obs if m_obs else 'Registro manual por contingencia'
                            }
                            try:
                                dp.save_manual_supernumerary(st.session_state.excel_path, doc_data)
                                st.success(f"Médico {m_nombre} registrado correctamente por contingencia. Sincronizado en SharePoint.")
                                load_app_data()
                                st.rerun()
                            except Exception as ex_m:
                                st.error(f"Error al guardar registro manual: {ex_m}")

            # Mostrar registros manuales activos para poder retirarlos si ya están en SharePoint
            try:
                df_man = dp.load_manual_supernumeraries(st.session_state.excel_path)
                if not df_man.empty:
                    st.markdown("##### 📝 Médicos Registrados Manualmente por Contingencia")
                    for _, r_man in df_man.iterrows():
                        col_m_info, col_m_btn = st.columns([3, 1])
                        with col_m_info:
                            st.markdown(f"• **{r_man['NOMBRES Y APELLIDOS']}** (CC: {r_man['CEDULA']}) | Sede: {r_man['SEDE / CECO']}")
                        with col_m_btn:
                            if st.button("Desactivar", key=f"deact_{r_man['CEDULA']}", use_container_width=True):
                                dp.deactivate_manual_supernumerary(st.session_state.excel_path, r_man['CEDULA'])
                                st.success(f"Médico {r_man['NOMBRES Y APELLIDOS']} desactivado del registro manual.")
                                load_app_data()
                                st.rerun()
            except Exception:
                pass
                        
        with col_hist:
            st.markdown("#### 📜 Historial de Actividad (Últimos Movimientos)")
            try:
                df_hist = dp.load_modifications(st.session_state.excel_path)
                if not df_hist.empty and 'TIMESTAMP' in df_hist.columns:
                    df_hist_show = df_hist.sort_values(by='ID', ascending=False).head(15)
                    for _, r_hist in df_hist_show.iterrows():
                        fecha_accion = r_hist['TIMESTAMP']
                        tipo = r_hist['TYPE']
                        doc_inv = r_hist['NEW_NAME'] if r_hist['NEW_NAME'] else r_hist['ORIGINAL_NAME']
                        dia_afectado = r_hist['DATE'].strftime('%d/%m/%Y') if pd.notna(r_hist['DATE']) else ""
                        icon = "➕" if tipo == "AGREGAR" else ("❌" if tipo == "ELIMINAR" else "🔄")
                        st.markdown(f"- **{fecha_accion}** | {icon} **{tipo}**: {doc_inv} en la fecha {dia_afectado}")
                else:
                    st.write("No hay historial reciente registrado.")
            except Exception:
                st.write("El historial no está disponible actualmente.")

# Footer
st.markdown(
    """
    <div class='app-footer'>
        © 2026 - San Vicente CES
    </div>
    """, 
    unsafe_allow_html=True
)