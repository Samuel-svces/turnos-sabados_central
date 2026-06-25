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
        df_super = dp.load_supernumeraries(st.session_state.excel_path)
        st.session_state.super_df = df_super
        
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
    with st.popover("⚙️", help="Administración"):
        st.markdown("#### <i class='bi bi-shield-lock-fill'></i> Acceso Administrador", unsafe_allow_html=True)
        
        if st.session_state.is_admin:
            st.success("Sesión Iniciada (Admin)")
            if st.button("Cerrar Sesión", use_container_width=True, key="btn_popover_logout"):
                st.session_state.is_admin = False
                st.rerun()
        else:
            admin_password = "Central1234.*"
            try:
                if "admin_password" in st.secrets:
                    admin_password = st.secrets["admin_password"]
            except Exception:
                pass
                
            pwd_input = st.text_input("Contraseña de Admin:", type="password", key="admin_pwd_popover")
            if st.button("Iniciar Sesión", use_container_width=True, key="btn_popover_login"):
                if pwd_input == admin_password:
                    st.session_state.is_admin = True
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta")

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

from streamlit_sortables import sort_items

with tab_calendar:
    if not st.session_state.is_admin:
        st.info("Cualquier solicitud de cambio de turno o cambio de secuencia, favor enviar correo a **central@sanvicenteces.com**. Una vez sea aceptado por el correo, se verá reflejado en este cuadro.")
    
    if st.session_state.is_admin and st.session_state.last_action is not None:
        if st.button("↩️ Deshacer Último Movimiento", type="secondary", use_container_width=False):
            la = st.session_state.last_action
            try:
                if la['action'] == 'ELIMINAR':
                    dp.add_shift_to_date(la['excel_path'], la['sheet'], la['date'], la['doc'], la.get('obs', ''), la.get('clasificacion', 'Secuencia Normal'))
                    st.success("Acción revertida: Médico re-agregado.")
                elif la['action'] == 'AGREGAR':
                    # Need to delete it. We know date and doc.
                    dp.delete_shift_cell(la['excel_path'], la['sheet'], 0, 0, la['date'], "", la['doc'], la.get('clasificacion', 'Secuencia Normal'))
                    st.success("Acción revertida: Médico eliminado del día.")
                elif la['action'] == 'MOVE':
                    # Delete from new_date, add to old_date
                    dp.delete_shift_cell(la['excel_path'], la['sheet'], 0, 0, la['new_date'], "", la['doc'], la.get('clasificacion', 'Secuencia Normal'))
                    dp.add_shift_to_date(la['excel_path'], la['sheet'], la['old_date'], la['doc'], la.get('obs', ''), la.get('clasificacion', 'Secuencia Normal'))
                    st.success("Acción revertida: Movimiento cancelado.")
                
                st.session_state.last_action = None
                load_app_data()
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo deshacer: {e}")

    if "search_input" not in st.session_state:
        st.session_state["search_input"] = ""

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
        st.button("B", key="btn_search", use_container_width=True)
    with col_btn_clear:
        st.button("L", key="btn_clear", use_container_width=True, on_click=clear_search)
    with col_refresh:
        st.button("R", key="btn_refresh", help="Recargar datos", use_container_width=True, on_click=refresh_data)

    st.components.v1.html("""
    <script>
    function styleButtons() {
        // 1. Estilizar botones de la barra de búsqueda
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(btn => {
            const text = btn.innerText.trim();
            if(text === 'B') {
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="1.2rem" height="1.2rem"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/></svg>';
                btn.classList.add('custom-btn-search');
                btn.style.color = 'transparent';
                btn.style.display = 'flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.removeProperty('background-color');
                btn.style.removeProperty('border-color');
                btn.style.removeProperty('background');
            } else if(text === 'L') {
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="1.2rem" height="1.2rem"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/><path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/></svg>';
                btn.classList.add('custom-btn-clear');
                btn.style.color = 'transparent';
                btn.style.display = 'flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.removeProperty('background-color');
                btn.style.removeProperty('border-color');
                btn.style.removeProperty('background');
            } else if(text === 'R') {
                btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="1.2rem" height="1.2rem"><path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"/><path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"/></svg>';
                btn.classList.add('custom-btn-refresh');
                btn.style.color = 'transparent';
                btn.style.display = 'flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.removeProperty('background-color');
                btn.style.removeProperty('border-color');
                btn.style.removeProperty('background');
            } else if(text === 'Iniciar Sesión') {
                btn.classList.add('custom-btn-login');
                btn.style.removeProperty('background-color');
                btn.style.removeProperty('border-color');
                btn.style.removeProperty('background');
                btn.style.removeProperty('color');
            }
        });

        // 2. Estilizar tarjetas de sortables (drag & drop) en modo Administrador
        const iframes = window.parent.document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (!iframeDoc) return;
                
                const elements = iframeDoc.querySelectorAll('div, span, li, p');
                elements.forEach(el => {
                    if (el.innerText && el.innerText.trim().startsWith('🎯')) {
                        // Estilos para el elemento de texto
                        el.style.setProperty('background-color', '#fff8e1', 'important');
                        el.style.setProperty('color', '#e65100', 'important');
                        el.style.setProperty('border-color', '#ffc107', 'important');
                        el.style.setProperty('box-shadow', '0 0 12px rgba(255, 193, 7, 0.4)', 'important');
                        el.style.setProperty('font-weight', '700', 'important');
                        
                        // Propagar los estilos a los contenedores padre para colorear la tarjeta completa
                        let parent = el.parentElement;
                        for (let d = 0; d < 2; d++) {
                            if (parent && parent.tagName !== 'BODY') {
                                parent.style.setProperty('background-color', '#fff8e1', 'important');
                                parent.style.setProperty('color', '#e65100', 'important');
                                parent.style.setProperty('border-color', '#ffc107', 'important');
                                parent = parent.parentElement;
                            }
                        }
                    }
                });
            } catch (e) {
                // Evitar errores de sandbox de iframe
            }
        });
    }
    styleButtons();
    const observer = new MutationObserver(styleButtons);
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """, height=0)

    if search_query:
        found = False
        if not df_shifts.empty and df_shifts['Supernumerary'].str.upper().str.contains(search_query, na=False).any():
            found = True
            
        if not found:
            st.components.v1.html(f"""
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
                Swal.fire({{
                    icon: 'warning',
                    title: 'No encontrado',
                    text: 'El nombre "{search_query}" no está en la base de datos de turnos.',
                    confirmButtonColor: '#1a73e8'
                }});
            </script>
            """, height=0)

    today = datetime.date.today()
    days_to_sat = (5 - today.weekday()) % 7
    first_sat = today + datetime.timedelta(days=days_to_sat)
    generated_sats = [first_sat + datetime.timedelta(weeks=w) for w in range(52)]
    
    db_future_sats = []
    if not df_shifts.empty and 'Date' in df_shifts.columns:
        db_future_sats = [d for d in df_shifts['Date'].unique() if d >= today]
    
    all_future_saturdays = sorted(list(set(db_future_sats + generated_sats)))
    
    if not all_future_saturdays:
        st.info("No se encontraron turnos de sábados futuros programados.")
    else:
        if st.session_state.is_admin:
            if 'saturday_offset' not in st.session_state:
                st.session_state.saturday_offset = 0
            
            if st.session_state.saturday_offset >= len(all_future_saturdays):
                st.session_state.saturday_offset = max(0, ((len(all_future_saturdays) - 1) // 4) * 4)
                
            offset = st.session_state.saturday_offset
            saturdays = all_future_saturdays[offset:offset+4]
            
            col_nav_prev, col_nav_info, col_nav_next = st.columns([1.2, 2, 1.2])
            with col_nav_prev:
                has_prev = offset > 0
                if st.button("◀ Sábados Anteriores", use_container_width=True, disabled=not has_prev, key="btn_prev_sats"):
                    st.session_state.saturday_offset = max(0, offset - 4)
                    st.rerun()
            with col_nav_info:
                start_sat = offset + 1
                end_sat = min(len(all_future_saturdays), offset + 4)
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 0.5rem; color: #1565c0; font-family: Outfit; font-size: 1.05rem;'>Sábados {start_sat} a {end_sat} de {len(all_future_saturdays)} futuros</div>", unsafe_allow_html=True)
            with col_nav_next:
                has_next = offset + 4 < len(all_future_saturdays)
                if st.button("Siguientes Sábados ▶", use_container_width=True, disabled=not has_next, key="btn_next_sats"):
                    st.session_state.saturday_offset = offset + 4
                    st.rerun()
        else:
            saturdays = all_future_saturdays[:4]
            
        month_shifts = df_shifts[df_shifts['Date'].isin(saturdays)] if not df_shifts.empty else pd.DataFrame()
        
        if st.session_state.is_admin:
            st.markdown("<p style='text-align: center; color: #666; font-size: 0.95rem; margin-top: 1rem;'><i class='bi bi-info-circle'></i> <b>Modo Administrador:</b> Arrastra las tarjetas de los médicos entre las columnas para reasignar sus turnos.</p>", unsafe_allow_html=True)
            
            # Prepare sortable items
            original_state = []
            global_docs_seen = set()
            for sat_date in saturdays:
                date_shifts = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                
                header_text = sat_date.strftime('%d de %b, %Y').upper()
                is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                if is_holiday:
                    header_text += " (FESTIVO)"
                    
                docs = []
                for _, row in date_shifts.iterrows():
                    name = row['Supernumerary']
                    clasif = row.get('Classification', 'Secuencia Normal')
                    obs = str(row.get('Observation', '')) if pd.notna(row.get('Observation')) else ''
                    
                    personal_obs = ""
                    if not df_super.empty:
                        doc_match = df_super[df_super['NOMBRES Y APELLIDOS'] == name]
                        if not doc_match.empty:
                            personal_obs = str(doc_match.iloc[0].get('OBSERVACIONES', '')).strip()
                            
                    display_name = name
                    if "Compensación" in str(clasif):
                        display_name += " 🟡(COMP)"
                    elif obs or personal_obs:
                        display_name += " 💬"
                        
                    if search_query and search_query in name.upper():
                        display_name = "🎯 " + display_name
                        
                    # Evitar nombres duplicados GLOBALMENTE en todos los sábados (Error #185 de React)
                    original_display = display_name
                    counter = 1
                    while display_name in global_docs_seen:
                        display_name = original_display + ("\u200B" * counter)
                        counter += 1
                        
                    global_docs_seen.add(display_name)
                    docs.append(display_name)
                
                original_state.append({
                    'header': header_text,
                    'items': docs,
                    'date': sat_date.strftime('%Y-%m-%d')
                })
                
            # Render sortable columns inside container
            with st.container():
                st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
                returned_state = sort_items(
                    [{'header': c['header'], 'items': c['items']} for c in original_state],
                    multi_containers=True,
                    direction='horizontal',
                    key=f"sortable_sats_{offset}_{st.session_state.get('last_load_time', '0')}"
                )
            
            # Diff calculation to detect drag and drop
            if returned_state:
                moved_doc = None
                from_date = None
                to_date = None
                
                for i in range(len(original_state)):
                    orig_items = set(original_state[i]['items'])
                    new_items = set(returned_state[i]['items'])
                    
                    added = new_items - orig_items
                    removed = orig_items - new_items
                    
                    if removed:
                        from_date = original_state[i]['date']
                        moved_doc = list(removed)[0]
                    if added:
                        to_date = original_state[i]['date']
                        if not moved_doc:
                            moved_doc = list(added)[0]
                            
                if moved_doc and from_date and to_date and from_date != to_date:
                    # Execute DB Move
                    old_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                    new_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
                    
                    try:
                        # 1. Find the old shift details
                        # Remove emojis, zero-width spaces, and search highlight to get raw name
                        raw_name = moved_doc.replace("🎯 ", "").split(" 🟡")[0].split(" 💬")[0].replace("\u200B", "")
                        old_row = df_shifts[(df_shifts['Date'] == old_date) & (df_shifts['Supernumerary'] == raw_name)].iloc[0]
                        sheet = old_row['Sheet']
                        r_idx = int(old_row['Excel_Row'])
                        c_idx = int(old_row['Excel_Col'])
                        obs = str(old_row.get('Observation', '')) if pd.notna(old_row.get('Observation')) else ''
                        clasif = old_row.get('Classification', 'Secuencia Normal')
                        
                        # 2. Check if the doc is already in the new date (duplicate)
                        new_date_shifts = month_shifts[month_shifts['Date'] == new_date]
                        if not new_date_shifts.empty and raw_name in new_date_shifts['Supernumerary'].values:
                            st.error(f"¡El médico {moved_doc} ya tiene un turno el {to_date}! Movimiento cancelado.")
                            st.rerun()
                            
                        # GUARDAR ACCION EN LAST_ACTION PARA UNDO
                        st.session_state.last_action = {
                            'action': 'MOVE',
                            'excel_path': st.session_state.excel_path,
                            'sheet': sheet,
                            'old_row': r_idx,
                            'old_col': c_idx,
                            'old_date': old_date,
                            'new_date': new_date,
                            'doc': raw_name,
                            'obs': obs,
                            'clasificacion': clasif
                        }
                            
                        # 3. Delete old
                        dp.delete_shift_cell(
                            excel_path=st.session_state.excel_path,
                            sheet_name=sheet,
                            row_idx=r_idx,
                            col_idx=c_idx,
                            date_val=old_date,
                            observation="",
                            original_name=raw_name,
                            clasificacion="Secuencia Normal"
                        )
                        
                        # 4. Add new
                        target_sheet = sheet
                        dp.add_shift_to_date(
                            excel_path=st.session_state.excel_path,
                            sheet_name=target_sheet,
                            target_date=new_date,
                            supernumerary_name=raw_name,
                            observation=obs,
                            clasificacion=clasif
                        )
                        
                        st.success("Cambios consolidados correctamente en la nube.")
                        load_app_data()
                        st.rerun()

                        
                    except Exception as e:
                        st.error(f"Error al mover el turno: {e}")
                        
            st.markdown("---")
            with st.expander("Modificar Detalles / Eliminar / Agregar Médico (Avanzado)"):
                st.info("Para editar clasificaciones, ver detalles o agregar un médico manualmente, usa las opciones de abajo.")
                cols_adv = st.columns(len(saturdays))
                for idx, sat_date in enumerate(saturdays):
                    with cols_adv[idx]:
                        st.markdown(f"**{sat_date.strftime('%d/%m')}**")
                        date_shifts = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                        for d_idx, s_row in date_shifts.reset_index().iterrows():
                            name = s_row['Supernumerary']
                            if st.button(f"Editar {name}", key=f"edit_btn_{sat_date}_{name}_{d_idx}"):
                                action_details = {
                                    'date': sat_date,
                                    'doctor': name,
                                    'row': int(s_row['Excel_Row']),
                                    'col': int(s_row['Excel_Col']),
                                    'sheet': s_row['Sheet']
                                }
                                ui_dialogs.show_selection_dialog(action_details, load_app_data)
                                
                        st.markdown("<div class='add-doc-btn-wrapper'></div>", unsafe_allow_html=True)
                        if st.button("Agregar Médico", key=f"add_btn_{sat_date}", use_container_width=True):
                            sheet_name = date_shifts.iloc[0]['Sheet'] if not date_shifts.empty else f"SABADOS {sat_date.year}"
                            ui_dialogs.show_add_dialog(sat_date, sheet_name, load_app_data)

        else:
            # PUBLIC VIEW: Read-Only Grid inside container
            with st.container():
                st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
                st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
                cols = st.columns(len(saturdays))
                for idx, sat_date in enumerate(saturdays):
                    with cols[idx]:
                        is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                        holiday_class = " holiday" if is_holiday else ""
                        
                        date_shifts = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                        num_doctors = len(date_shifts)
                        
                        header_text = sat_date.strftime('%d de %b, %Y').upper()
                        header_text += f" ({num_doctors} Médicos)"
                        if is_holiday:
                            header_text += " (FESTIVO)"
                            
                        st.markdown(f"<div class='saturday-col'><div class='sat-header{holiday_class}'>{header_text}</div>", unsafe_allow_html=True)
                        
                        for _, s_row in date_shifts.reset_index().iterrows():
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
                            
                            st.markdown(f"<div class='doc-btn-wrap'><div class='{badge_classes}'>{obs_dot}{name}</div>{tooltip_html}</div>", unsafe_allow_html=True)
                            
                        st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


# ----------------- TAB 3: ADMIN CONTROL PANEL -----------------
if st.session_state.is_admin:
    with tab_admin:
        st.markdown("### <i class='bi bi-sliders2'></i> Directorio de Personal y Sincronización", unsafe_allow_html=True)
        st.markdown("Gestión de altas, bajas y modificaciones en el directorio de médicos supernumerarios, y sincronización con el repositorio Excel.")
        
        col_dir, col_sync = st.columns([1.2, 1])
        
        with col_dir:
            st.markdown("#### <i class='bi bi-person-gear'></i> Gestión del Directorio de Médicos", unsafe_allow_html=True)
            admin_doc_action = st.selectbox("Seleccione Acción de Personal:", ["Registrar Nuevo Médico", "Modificar Médico Existente", "Desactivar Médico"])
            
            if admin_doc_action == "Registrar Nuevo Médico":
                with st.form("admin_add_doc_form", clear_on_submit=True):
                    new_cedula = st.text_input("Cédula / Identificación:")
                    new_name = st.text_input("Nombre Completo (APELLIDOS NOMBRES):")
                    
                    _today = datetime.date.today()
                    _next_sat = _today + datetime.timedelta(days=(5 - _today.weekday()) % 7 or 7)
                    new_fecha_inicio = st.date_input(
                        "Fecha de inicio en la secuencia:",
                        value=_next_sat,
                        help="Sábado a partir del cual este médico empieza a aparecer en la rotación de turnos."
                    )
                    new_obs = st.text_area(
                        "Observaciones (opcional):",
                        placeholder="Ej: Médico nuevo desde julio 2026, referido por Dr. García...",
                        height=80
                    )
                    
                    submit_add_doc = st.form_submit_button("Agregar Médico al Directorio", use_container_width=True)
                    if submit_add_doc:
                        if not new_cedula.strip() or not new_name.strip():
                            st.error("Cédula y Nombre Completo son obligatorios.")
                        else:
                            p_data = {
                                'cedula': new_cedula.strip(),
                                'nombres_y_apellidos': new_name.strip().upper(),
                                'cargo': "MEDICO SUPERNUMERARIO",
                                'celular': "",
                                'sede_ceco': "SUPERNUMERARIOS",
                                'status': 'ACTIVO',
                                'type': 'AGREGAR',
                                'fecha_inicio': new_fecha_inicio,
                                'observaciones': new_obs.strip()
                            }
                            try:
                                dp.save_personal_modification(st.session_state.excel_path, p_data)
                            except PermissionError:
                                st.error("⚠️ Error de Permisos: El archivo de Excel está abierto en otra aplicación. Por favor, ciérralo y vuelve a intentarlo.")
                                st.stop()
                            msg = f"Médico {new_name.upper()} agregado con éxito. Inicio de secuencia: {new_fecha_inicio.strftime('%d/%m/%Y')}."
                            if new_obs.strip():
                                msg += f" | Obs: {new_obs.strip()}"
                            st.success(msg)
                            load_app_data()
                            st.rerun()
                            
            elif admin_doc_action == "Modificar Médico Existente":
                known_docs_mod = df_super['NOMBRES Y APELLIDOS'].tolist()
                selected_doc_mod = st.selectbox("Seleccione Médico a Modificar:", known_docs_mod)
                doc_row = df_super[df_super['NOMBRES Y APELLIDOS'] == selected_doc_mod].iloc[0]
                
                df_pm_check = dp.load_personal_modifications(st.session_state.excel_path)
                pm_match = df_pm_check[df_pm_check['CEDULA'] == str(doc_row['CEDULA'])]
                existing_fecha = None
                if not pm_match.empty and pm_match.iloc[-1]['FECHA_INICIO'] is not None:
                    try:
                        existing_fecha = pm_match.iloc[-1]['FECHA_INICIO']
                    except Exception:
                        existing_fecha = None
                
                _today2 = datetime.date.today()
                _default_fecha = existing_fecha if existing_fecha else _today2
                
                with st.form("admin_edit_doc_form", clear_on_submit=True):
                    edit_cedula = st.text_input("Cédula (No editable):", value=str(doc_row['CEDULA']), disabled=True)
                    edit_name = st.text_input("Nombre Completo:", value=str(doc_row['NOMBRES Y APELLIDOS']))
                    edit_fecha_inicio = st.date_input(
                        "Fecha de inicio en la secuencia:",
                        value=_default_fecha,
                        help="Sábado a partir del cual este médico aparece en la rotación."
                    )
                    edit_obs = st.text_area(
                        "Observaciones (opcional):",
                        placeholder="Ej: Actualización de nombre por cambio de documento...",
                        height=80
                    )
                    
                    submit_edit_doc = st.form_submit_button("Guardar Cambios en Delta", use_container_width=True)
                    if submit_edit_doc:
                        if not edit_name.strip():
                            st.error("El nombre completo no puede estar vacío.")
                        else:
                            p_data = {
                                'cedula': edit_cedula.strip(),
                                'nombres_y_apellidos': edit_name.strip().upper(),
                                'cargo': str(doc_row['CARGO']).strip().upper(),
                                'celular': str(doc_row['CELULAR']).strip(),
                                'sede_ceco': str(doc_row['SEDE / CECO']).strip().upper(),
                                'status': 'ACTIVO',
                                'type': 'MODIFICAR',
                                'fecha_inicio': edit_fecha_inicio,
                                'observaciones': edit_obs.strip()
                            }
                            try:
                                dp.save_personal_modification(st.session_state.excel_path, p_data)
                            except PermissionError:
                                st.error("⚠️ Error de Permisos: El archivo de Excel está abierto en otra aplicación. Por favor, ciérralo y vuelve a intentarlo.")
                                st.stop()
                            msg = f"Cambios para {edit_name.upper()} registrados. Inicio de secuencia: {edit_fecha_inicio.strftime('%d/%m/%Y')}."
                            if edit_obs.strip():
                                msg += f" | Obs: {edit_obs.strip()}"
                            st.success(msg)
                            load_app_data()
                            st.rerun()
                            
            elif admin_doc_action == "Desactivar Médico":
                known_docs_del = df_super['NOMBRES Y APELLIDOS'].tolist()
                selected_doc_del = st.selectbox("Seleccione Médico a Desactivar:", ["-- Seleccionar Médico --"] + known_docs_del)
                
                if selected_doc_del != "-- Seleccionar Médico --":
                    doc_row = df_super[df_super['NOMBRES Y APELLIDOS'] == selected_doc_del].iloc[0]
                    st.warning(f"¿Está seguro que desea desactivar a **{selected_doc_del}** (Cédula: {doc_row['CEDULA']})? Ya no aparecerá en el directorio activo ni para nuevas asignaciones, pero se mantendrá su historial.")
                    
                    if st.button("Confirmar Desactivación", use_container_width=True):
                        p_data = {
                            'cedula': str(doc_row['CEDULA']).strip(),
                            'nombres_y_apellidos': str(doc_row['NOMBRES Y APELLIDOS']).strip().upper(),
                            'cargo': str(doc_row['CARGO']).strip().upper(),
                            'celular': str(doc_row['CELULAR']).strip(),
                            'sede_ceco': str(doc_row['SEDE / CECO']).strip().upper(),
                            'status': 'INACTIVO',
                            'type': 'DESACTIVAR'
                        }
                        try:
                            dp.save_personal_modification(st.session_state.excel_path, p_data)
                        except PermissionError:
                            st.error("⚠️ Error de Permisos: El archivo de Excel está abierto en otra aplicación. Por favor, ciérralo y vuelve a intentarlo.")
                            st.stop()
                        st.success(f"Médico {selected_doc_del} marcado como INACTIVO.")
                        load_app_data()
                        st.rerun()
                        
        with col_sync:
            st.markdown("#### <i class='bi bi-cloud-upload'></i> Guardado y Consolidación", unsafe_allow_html=True)
            st.markdown("Las modificaciones de turnos y personal realizadas se registran al instante en la aplicación en archivos delta temporales.")
            st.markdown("Para guardar de forma física y permanente en el archivo de Excel master y consolidar los cambios, haz clic en el botón de abajo.")
            
            df_m_del = dp.load_modifications(st.session_state.excel_path)
            df_p_del = dp.load_personal_modifications(st.session_state.excel_path)
            pending_count = len(df_m_del) + len(df_p_del)
            
            if pending_count > 0:
                st.warning(f"Tienes **{pending_count}** cambios pendientes por consolidar en el Excel principal.")
            else:
                st.info("Todos los cambios están consolidados. El repositorio Excel está al día.")
                
            if st.button("Consolidar cambios en Excel Principal", use_container_width=True, disabled=pending_count==0, key="btn_consolidate_tab"):
                with st.spinner("Guardando y consolidando cambios en el archivo master..."):
                    try:
                        dp.consolidate_changes_to_excel(st.session_state.excel_path)
                        st.success("¡Todos los cambios han sido consolidados y escritos con éxito en el archivo máster 'TURNOS SABADOS.xlsx'!")
                        load_app_data()
                        st.rerun()
                    except PermissionError:
                        st.error("Error de Permisos: El archivo de Excel master ('TURNOS SABADOS.xlsx') está abierto o bloqueado por otra aplicación. Por favor, ciérralo y vuelve a intentarlo.")
                    except Exception as e:
                        st.error(f"Error al consolidar: {e}")
                        
            st.markdown("---")
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