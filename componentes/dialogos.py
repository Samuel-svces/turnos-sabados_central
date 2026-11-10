import streamlit as st
import datetime
try:
    from modulos import procesador_datos as dp
except Exception:
    import data_processor as dp
import pandas as pd

def get_allowed_doctors(target_date=None):
    """
    Retorna el listado de médicos supernumerarios disponibles para asignación o reemplazo.
    Carga exclusivamente los supernumerarios activos que cumplan con la condición estricta:
    Cédula llena (no vacía) y fecha de 01/10/2026 en adelante (sin incluir registros anteriores).
    """
    df_sup = st.session_state.get('super_df', pd.DataFrame())
    
    docs_set = set()
    invalid_names = {
        "VALENCIA", "MES:", "SABADOS", "TOTAL", "CANTIDAD",
        "SIN SUPERNUMERARIO", "SIN AGENDA", "AGENDA EN VACACIONES", "ELIMINAR"
    }

    # Cargar exclusivamente los supernumerarios activos y validados del directorio
    if isinstance(df_sup, pd.DataFrame) and not df_sup.empty:
        col_name = 'Profesional' if 'Profesional' in df_sup.columns else ('NOMBRES Y APELLIDOS' if 'NOMBRES Y APELLIDOS' in df_sup.columns else None)
        col_ced = 'Cédula' if 'Cédula' in df_sup.columns else ('CEDULA' if 'CEDULA' in df_sup.columns else None)
        if col_name:
            for _, r in df_sup.iterrows():
                # Verificar cédula obligatoria
                ced_val = str(r.get(col_ced, '')).strip().replace('.0', '') if col_ced else ''
                if not ced_val or ced_val.lower() in ('nan', 'none', 'null', '0', ''):
                    continue
                clean_n = dp.normalize_name_no_accents(str(r[col_name])).strip().upper()
                if len(clean_n) > 2 and clean_n not in invalid_names and not clean_n.startswith("CONSOLIDADO"):
                    docs_set.add(clean_n)

    return sorted(list(docs_set))

def save_changes_callback(excel_path, sheet, row, col, date_val, original_name, new_name, observation, classification, current_clasif, swap_target, current_doc, load_app_data_func):
    try:
        # Asegurarnos de que date_val sea datetime.date
        date_check = date_val
        if isinstance(date_check, datetime.datetime):
            date_check = date_check.date()
        elif isinstance(date_check, str):
            date_check = pd.to_datetime(date_check).date()

        mods_list = []

        # 1. Limpiar contraparte anterior si esta asignación ya tenía un cambio registrado
        if "Cambio de turno con" in current_clasif:
            old_counterpart = current_clasif.replace("Cambio de turno con ", "").strip().upper()
            df_s = st.session_state.shifts_df
            match_counterpart = df_s[
                (df_s['Supernumerary'].astype(str).str.strip().str.upper() == old_counterpart) & 
                (df_s['Classification'].str.contains(current_doc, na=False))
            ]
            for _, r_match in match_counterpart.iterrows():
                mods_list.append({
                    'sheet': r_match['Sheet'],
                    'date': r_match['Date'],
                    'original_name': r_match['Supernumerary'],
                    'new_name': r_match['Supernumerary'],
                    'row': int(r_match['Excel_Row']),
                    'col': int(r_match['Excel_Col']),
                    'type': 'REEMPLAZAR',
                    'observaciones': r_match.get('Observation', ''),
                    'clasificacion': 'Secuencia Normal'
                })
        
        # 2. Guardar cambios del turno
        if classification == "Cambio de turno" and swap_target:
            # Guardar médico de origen (toma el nombre del destino)
            mods_list.append({
                'sheet': sheet,
                'date': date_val,
                'original_name': current_doc,
                'new_name': swap_target['doctor'],
                'row': row,
                'col': col,
                'type': 'REEMPLAZAR',
                'observaciones': observation.strip(),
                'clasificacion': f"Cambio de turno con {swap_target['doctor']}"
            })
            
            # Guardar médico de destino (toma el nombre del origen)
            mods_list.append({
                'sheet': swap_target['sheet'],
                'date': swap_target['date'],
                'original_name': swap_target['doctor'],
                'new_name': current_doc,
                'row': swap_target['row'],
                'col': swap_target['col'],
                'type': 'REEMPLAZAR',
                'observaciones': observation.strip(),
                'clasificacion': f"Cambio de turno con {current_doc}"
            })
            st.session_state["show_swap_success_alert"] = True
            st.session_state["swap_doc_1"] = current_doc
            st.session_state["swap_doc_2"] = swap_target['doctor']
            st.session_state["swap_alert_counter"] = st.session_state.get("swap_alert_counter", 0) + 1
        else:
            mods_list.append({
                'sheet': sheet,
                'date': date_val,
                'original_name': original_name,
                'new_name': new_name,
                'row': row,
                'col': col,
                'type': 'ELIMINAR' if not new_name else 'REEMPLAZAR',
                'observaciones': observation.strip(),
                'clasificacion': classification
            })
            st.session_state["show_edit_success_alert"] = True
            st.session_state["edited_doc_name"] = new_name
            st.session_state["edit_alert_counter"] = st.session_state.get("edit_alert_counter", 0) + 1
            
        if mods_list:
            dp.save_modifications_batch(excel_path, mods_list)
            # Actualización optimista instantánea en memoria
            try:
                df_s = st.session_state.shifts_df.copy()
                df_s_dates = pd.to_datetime(df_s['Date'], errors='coerce').dt.date
                
                if classification == "Cambio de turno" and swap_target:
                    # Actualizar turno origen
                    mask_orig = (
                        (df_s['Sheet'] == sheet) & 
                        (df_s['Excel_Row'] == row) & 
                        (df_s['Excel_Col'] == col) & 
                        (df_s_dates == date_check)
                    ) if row > 0 and col > 0 else (
                        (df_s['Sheet'] == sheet) & 
                        (df_s_dates == date_check) & 
                        (df_s['Supernumerary'].astype(str).str.strip().str.upper() == str(current_doc).strip().upper())
                    )
                    df_s.loc[mask_orig, 'Supernumerary'] = str(swap_target['doctor']).strip().upper()
                    df_s.loc[mask_orig, 'Observation'] = observation.strip()
                    df_s.loc[mask_orig, 'Classification'] = f"Cambio de turno con {swap_target['doctor']}"
                    
                    # Actualizar turno destino
                    sw_date = swap_target['date']
                    if isinstance(sw_date, datetime.datetime):
                        sw_date = sw_date.date()
                    elif isinstance(sw_date, str):
                        sw_date = pd.to_datetime(sw_date).date()
                    
                    sw_row = swap_target.get('row', 0)
                    sw_col = swap_target.get('col', 0)
                    mask_dest = (
                        (df_s['Sheet'] == swap_target['sheet']) & 
                        (df_s['Excel_Row'] == sw_row) & 
                        (df_s['Excel_Col'] == sw_col) & 
                        (df_s_dates == sw_date)
                    ) if sw_row > 0 and sw_col > 0 else (
                        (df_s['Sheet'] == swap_target['sheet']) & 
                        (df_s_dates == sw_date) & 
                        (df_s['Supernumerary'].astype(str).str.strip().str.upper() == str(swap_target['doctor']).strip().upper())
                    )
                    df_s.loc[mask_dest, 'Supernumerary'] = str(current_doc).strip().upper()
                    df_s.loc[mask_dest, 'Observation'] = observation.strip()
                    df_s.loc[mask_dest, 'Classification'] = f"Cambio de turno con {current_doc}"
                else:
                    mask_edit = (
                        (df_s['Sheet'] == sheet) & 
                        (df_s['Excel_Row'] == row) & 
                        (df_s['Excel_Col'] == col) & 
                        (df_s_dates == date_check)
                    ) if row > 0 and col > 0 else (
                        (df_s['Sheet'] == sheet) & 
                        (df_s_dates == date_check) & 
                        (df_s['Supernumerary'].astype(str).str.strip().str.upper() == str(original_name).strip().upper())
                    )
                    if new_name:
                        df_s.loc[mask_edit, 'Supernumerary'] = str(new_name).strip().upper()
                        df_s.loc[mask_edit, 'Observation'] = observation.strip()
                        df_s.loc[mask_edit, 'Classification'] = classification
                    else:
                        df_s = df_s.drop(index=df_s[mask_edit].index).reset_index(drop=True)
                
                st.session_state.shifts_df = df_s
                dp.load_modifications.clear()
            except Exception as e_mem:
                print(f"Aviso actualizando memoria tras guardar cambios: {e_mem}")
            
        st.session_state.show_delete_options = False
        st.session_state.should_rerun_main = True
        st.rerun()
    except Exception as e:
        st.session_state.last_error = f"Error al guardar cambios: {e}"
        st.rerun()

def delete_shift_callback(excel_path, sheet, row, col, date_val, current_doc, current_clasif, load_app_data_func, scope="Eliminar de todas las secuencias (las futuras)"):
    st.session_state["is_deleting_processing"] = True
    try:
        df_s = st.session_state.shifts_df
        # Leer la opción seleccionada por el usuario con fallback a scope
        del_scope = st.session_state.get("del_scope_radio_flat", scope)
        
        # Asegurarnos de que date_val sea datetime.date
        date_check = date_val
        if isinstance(date_check, datetime.datetime):
            date_check = date_check.date()
        elif isinstance(date_check, str):
            date_check = pd.to_datetime(date_check).date()

        # Convertir a datetime.date para comparación segura
        df_s_dates = pd.to_datetime(df_s['Date'], errors='coerce').dt.date
        df_s_supers = df_s['Supernumerary'].astype(str).str.strip().str.upper()
        doc_clean = str(current_doc).strip().upper()

        if del_scope == "Eliminar de todas las secuencias (las futuras)":
            shifts_to_delete = df_s[
                (df_s_supers == doc_clean) & 
                (df_s_dates >= date_check)
            ]
        else:
            if row > 0 and col > 0:
                shifts_to_delete = df_s[
                    (df_s['Sheet'] == sheet) &
                    (df_s['Excel_Row'] == row) &
                    (df_s['Excel_Col'] == col) &
                    (df_s_dates == date_check)
                ]
            else:
                shifts_to_delete = pd.DataFrame()

            # Fallback 1: buscar por sheet + fecha + médico
            if shifts_to_delete.empty:
                shifts_to_delete = df_s[
                    (df_s['Sheet'] == sheet) &
                    (df_s_dates == date_check) &
                    (df_s_supers == doc_clean)
                ]
            
            # Fallback 2: buscar SOLO por fecha + médico (cualquier sheet)
            if shifts_to_delete.empty:
                shifts_to_delete = df_s[
                    (df_s_dates == date_check) &
                    (df_s_supers == doc_clean)
                ]
        
        if shifts_to_delete.empty:
            st.session_state.last_error = "No se encontraron asignaciones coincidentes para eliminar."
            st.session_state["is_deleting_processing"] = False
            st.rerun()
        else:
            deleted_count = 0
            deleted_items_log = []
            mods_list = []
            
            for _, r_del in shifts_to_delete.iterrows():
                row_clasif = r_del.get('Classification', 'Secuencia Normal')
                
                # Limpiar contraparte si era un cambio de turno
                if "Cambio de turno con" in row_clasif:
                    old_counterpart = row_clasif.replace("Cambio de turno con ", "").strip().upper()
                    match_counterpart = df_s[
                        (df_s['Supernumerary'].astype(str).str.strip().str.upper() == old_counterpart) & 
                        (df_s['Classification'].str.contains(r_del['Supernumerary'], na=False))
                    ]
                    for _, cp_row in match_counterpart.iterrows():
                        mods_list.append({
                            'sheet': cp_row['Sheet'],
                            'date': cp_row['Date'],
                            'original_name': cp_row['Supernumerary'],
                            'new_name': cp_row['Supernumerary'],
                            'row': int(cp_row['Excel_Row']),
                            'col': int(cp_row['Excel_Col']),
                            'type': 'REEMPLAZAR',
                            'observaciones': cp_row.get('Observation', ''),
                            'clasificacion': 'Secuencia Normal'
                        })
                
                # Guardar log para deshacer
                deleted_items_log.append({
                    'sheet': r_del['Sheet'], 'date': r_del['Date'], 'doc': r_del['Supernumerary'],
                    'obs': r_del.get('Observation', ''), 'clasificacion': row_clasif
                })
                
                # Eliminar el turno
                mods_list.append({
                    'sheet': r_del['Sheet'],
                    'date': r_del['Date'],
                    'original_name': r_del['Supernumerary'],
                    'new_name': '',
                    'row': int(r_del['Excel_Row']),
                    'col': int(r_del['Excel_Col']),
                    'type': 'ELIMINAR',
                    'observaciones': '',
                    'clasificacion': row_clasif
                })
                deleted_count += 1
            
            if mods_list:
                dp.save_modifications_batch(excel_path, mods_list)
                # Actualización en memoria ultrarrápida para que la UI responda de inmediato
                try:
                    to_del_indices = list(shifts_to_delete.index)
                    st.session_state.shifts_df = st.session_state.shifts_df.drop(index=to_del_indices).reset_index(drop=True)
                    dp.load_modifications.clear()
                except Exception as e_del_mem:
                    print(f"Aviso actualizando memoria tras eliminar: {e_del_mem}")
            
            # Registrar última acción para deshacer
            st.session_state.last_action = {
                'action': 'ELIMINAR_LOTE' if del_scope == "Eliminar de todas las secuencias (las futuras)" else 'ELIMINAR_SIMPLE',
                'excel_path': excel_path,
                'sheet': sheet,
                'row': row,
                'col': col,
                'date': date_val,
                'doc': current_doc,
                'clasificacion': current_clasif,
                'deleted_items': deleted_items_log
            }
            
            st.session_state.show_delete_options = False
            st.session_state.should_rerun_main = True
            st.session_state["delete_alert_counter"] = st.session_state.get("delete_alert_counter", 0) + 1
            st.session_state["show_delete_success_alert"] = True
            st.session_state["deleted_doc_name"] = current_doc
            st.rerun()
    except Exception as e:
        st.session_state.last_error = f"Error al eliminar: {e}"
        st.rerun()
    finally:
        st.session_state["is_deleting_processing"] = False

def show_delete_options_callback():
    st.session_state.show_delete_options = True

def cancel_delete_options_callback():
    st.session_state.show_delete_options = False

@st.dialog("Gestión de Turno")
def show_shift_dialog(action_details, load_app_data_func):
    if not st.session_state.is_admin:
        st.error("Acceso denegado: Se requieren permisos de administrador.")
        st.stop()

    current_doc = action_details['doctor']

    # Mostrar cuadro de bloqueo total mientras se procesa la eliminación
    if st.session_state.get("is_deleting_processing", False):
        st.markdown(
            f"""
            <style>
            button[aria-label="Close"], button[aria-label="Cerrar"], button[title="Close"], button[title="Cerrar"],
            div[data-testid="stDialog"] button[aria-label="Close"], div[data-testid="stDialog"] header + button,
            div[role="dialog"] button[aria-label="Close"], button[kind="header-close"],
            div[data-testid="stModal"] button[aria-label="Close"], button[aria-label="close"] {{
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
                width: 0px !important;
                height: 0px !important;
                position: absolute !important;
                left: -9999px !important;
            }}
            div[data-testid="stModalBackdrop"], div[data-baseweb="modal-backdrop"] {{
                pointer-events: none !important;
            }}
            </style>
            <div style="background: linear-gradient(135deg, #fee2e2 0%, #fff1f2 100%); border: 3px solid #ef4444; border-radius: 16px; padding: 25px 18px; text-align: center; margin: 15px 0;">
                <div style="font-size: 42px; margin-bottom: 8px;">⏳</div>
                <h3 style="color: #991b1b; margin: 0 0 8px 0; font-weight: 800; font-size: 20px;">Sincronizando con SharePoint...</h3>
                <p style="color: #7f1d1d; margin: 0; font-size: 15px; font-weight: 600;">Eliminando a <b>{current_doc}</b> de todas las secuencias futuras.</p>
                <p style="color: #b91c1c; margin-top: 12px; font-size: 13px; font-weight: 700; background-color: #fca5a5; padding: 6px 14px; border-radius: 20px; display: inline-block;">🔒 La ventana está bloqueada hasta completar la actualización.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    if st.session_state.get("show_delete_success_alert", False):
        st.rerun()  # Cierra el diálogo; la alerta la renderiza app.py en el siguiente ciclo

    if st.session_state.get("last_error"):
        st.error(st.session_state.last_error)

    st.markdown(f"### ✏️ Editar Turno")
    st.write(f"**Fecha:** {action_details['date'].strftime('%d/%m/%Y')}")
    st.markdown("---")
    
    clasif_options = ["Secuencia Normal", "Compensación / Pago de turno", "Cambio de turno"]
    current_clasif = action_details.get('classification', 'Secuencia Normal')
    if "Compensación" in current_clasif:
        default_clasif_idx = 1
    elif "Cambio" in current_clasif:
        default_clasif_idx = 2
    else:
        default_clasif_idx = 0
    new_clasif = st.radio("Clasificación del Turno:", clasif_options, index=default_clasif_idx, horizontal=True)
    
    allowed = get_allowed_doctors(target_date=action_details.get('date'))
    current_doc = dp.normalize_name_no_accents(action_details['doctor'])
    if current_doc not in allowed:
        allowed = sorted(list(set(allowed + [current_doc])))
    try:
        default_idx = allowed.index(current_doc)
    except ValueError:
        default_idx = 0
        
    # Permitir seleccionar nuevo médico para reemplazo directo; solo deshabilitar si es Cambio de turno (gestionado por swap_target)
    new_doc = st.selectbox("Médico Programado:", allowed, index=default_idx, disabled=(new_clasif == "Cambio de turno"))
    new_obs = st.text_input("Observaciones:", value=action_details.get('observation', ''))
    
    swap_target = None
    if new_clasif == "Cambio de turno":
        df_s = st.session_state.shifts_df
        current_date = action_details['date']
        today = datetime.date.today()
        
        # Determinar la secuencia del sábado actual:
        # Los sábados se alternan cada 2 semanas (secuencia A = semana 1,3,5... / secuencia B = semana 2,4,6...)
        # Calculamos el número de semana ISO y si es par o impar
        # para identificar a cuál grupo pertenece el sábado actual.
        current_week_parity = (current_date.isocalendar()[1]) % 2  # 0 = par, 1 = impar
        
        # Solo sábados FUTUROS (> hoy) con paridad OPUESTA (secuencia contraria)
        future_opposite = df_s[
            (df_s['Date'] > today) &
            (df_s['Date'] != current_date) &
            (df_s['Date'].apply(lambda d: (d.isocalendar()[1]) % 2) != current_week_parity)
        ] if not df_s.empty else pd.DataFrame()
        
        if not future_opposite.empty:
            future_opposite = future_opposite.sort_values(by='Date')
            other_docs = []
            other_docs_map = {}
            for _, row in future_opposite.iterrows():
                doc_name = row['Supernumerary']
                d_val = row['Date']
                d_str = d_val.strftime('%d/%m/%Y')
                label = f"{doc_name} ({d_str})"
                # Evitar duplicados (mismo médico y misma fecha)
                if label not in other_docs_map:
                    other_docs.append(label)
                    other_docs_map[label] = {
                        'doctor': doc_name,
                        'date': d_val,
                        'sheet': row['Sheet'],
                        'row': int(row['Excel_Row']),
                        'col': int(row['Excel_Col']),
                        'classification': row.get('Classification', 'Secuencia Normal'),
                        'observation': row.get('Observation', '')
                    }
            # Ordenar cronológicamente por fecha (no alfabéticamente por label)
            other_docs = sorted(other_docs, key=lambda lbl: other_docs_map[lbl]['date'])
            
            if other_docs:
                default_other_idx = 0
                if "Cambio de turno con" in current_clasif:
                    match_name = current_clasif.replace("Cambio de turno con ", "").strip()
                    for idx, lbl in enumerate(other_docs):
                        if match_name in lbl:
                            default_other_idx = idx
                            break
                
                selected_swap_label = st.selectbox("Seleccione Médico con quien cambia:", other_docs, index=default_other_idx)
                swap_target = other_docs_map[selected_swap_label]
            else:
                st.info("No hay médicos en sábados futuros de la secuencia contraria disponibles para el cambio.")
        else:
            st.info("No hay médicos en sábados futuros de la secuencia contraria disponibles para el cambio.")
            
    # Gestión del estado de la confirmación de eliminación
    current_target = f"{action_details['date']}_{action_details['doctor']}"
    if st.session_state.get('prev_delete_target') != current_target:
        st.session_state.show_delete_options = False
        st.session_state.last_error = None
        st.session_state.prev_delete_target = current_target

    if st.session_state.get("show_delete_options", False):
        st.markdown("---")
        st.markdown(f"##### 🗑️ ¿Confirmar eliminación del turno de **{current_doc}**?")
        st.caption("Esta acción eliminará el turno para este sábado directamente en la Lista de SharePoint.")
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            st.button(
                "Confirmar Eliminación", 
                use_container_width=True, 
                type="primary", 
                key="btn_confirm_delete_action",
                on_click=delete_shift_callback,
                icon=":material/check_circle:",
                args=(
                    st.session_state.excel_path,
                    action_details['sheet'],
                    action_details['row'],
                    action_details['col'],
                    action_details['date'],
                    current_doc,
                    current_clasif,
                    load_app_data_func
                )
            )
        with col_cancel:
            st.button(
                "Cancelar", 
                use_container_width=True, 
                key="btn_cancel_delete_action",
                on_click=cancel_delete_options_callback,
                icon=":material/cancel:"
            )
    else:
        col_save, col_delete = st.columns([2, 1])
        with col_save:
            st.button(
                "Guardar Cambios", 
                use_container_width=True, 
                type="primary", 
                key="btn_save_changes_action",
                on_click=save_changes_callback,
                icon=":material/save:",
                args=(
                    st.session_state.excel_path,
                    action_details['sheet'],
                    action_details['row'],
                    action_details['col'],
                    action_details['date'],
                    current_doc,
                    new_doc,
                    new_obs,
                    new_clasif,
                    current_clasif,
                    swap_target,
                    current_doc,
                    load_app_data_func
                )
            )
        with col_delete:
            st.button(
                "Remover Turno", 
                use_container_width=True, 
                type="secondary", 
                key="btn_show_delete_options_action",
                on_click=show_delete_options_callback,
                icon=":material/delete:"
            )

@st.dialog("Agregar Médico Adicional")
def show_add_dialog(sat_date, sheet, load_app_data_func):
    if not st.session_state.is_admin:
        st.error("Acceso denegado: Se requieren permisos de administrador.")
        st.stop()
    st.markdown("### Asignar Médico Adicional")
    DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    fecha_es = f"{DIAS[sat_date.weekday()]}, {sat_date.day:02d} de {MESES[sat_date.month-1]} de {sat_date.year}"
    st.write(f"**Fecha:** {fecha_es}")
    st.markdown("---")
    
    df_s = st.session_state.shifts_df
    already_assigned = [dp.normalize_name_no_accents(n) for n in df_s[df_s['Date'] == sat_date]['Supernumerary'].tolist()]
    
    allowed = get_allowed_doctors(target_date=sat_date)
    
    # Buscador de médicos insensible a tildes y espacios
    search_doc = st.text_input(
        "Buscar Médico (nombre o cédula):",
        placeholder="Escriba para filtrar sin preocuparse por tildes ni espacios...",
        key=f"search_doc_add_{sat_date}"
    ).strip()
    
    filtered_allowed = allowed
    if search_doc:
        q_norm = dp.normalize_name_no_accents(search_doc)
        q_compact = q_norm.replace(" ", "")
        
        # Búsqueda por cédula en df_super si está disponible
        cedula_matches = set()
        df_sup = st.session_state.get('super_df', pd.DataFrame())
        if not df_sup.empty and 'CEDULA' in df_sup.columns:
            name_col = 'Profesional' if 'Profesional' in df_sup.columns else 'NOMBRES Y APELLIDOS'
            ced_mask = df_sup['CEDULA'].astype(str).str.contains(q_norm, na=False)
            cedula_matches = set(df_sup[ced_mask][name_col].dropna().apply(dp.normalize_name_no_accents).tolist())
        
        matched = []
        for doc in allowed:
            doc_norm = dp.normalize_name_no_accents(doc)
            doc_compact = doc_norm.replace(" ", "")
            if q_norm in doc_norm or q_compact in doc_compact or doc_norm in cedula_matches:
                matched.append(doc)
        
        if matched:
            filtered_allowed = matched
        else:
            st.info("No se encontraron coincidencias con el filtro. Mostrando lista completa.")
            filtered_allowed = allowed

    new_doc = st.selectbox("Seleccione Médico Supernumerario:", filtered_allowed)
    new_doc_norm = dp.normalize_name_no_accents(new_doc) if new_doc else ""
    obs = st.text_input("Observaciones (opcional):", placeholder="Ej: Pago de turno...")
    clasif = st.radio("Clasificación del Turno:", ["Secuencia Normal", "Compensación / Pago de turno"], horizontal=True)
    
    # Calcular sábados futuros del mismo ciclo biemanal (cada 14 días)
    is_secuencia_normal = (clasif == "Secuencia Normal")
    future_dates = []
    if is_secuencia_normal:
        candidate = sat_date + datetime.timedelta(weeks=2)
        end_date = sat_date + datetime.timedelta(weeks=52)
        while candidate <= end_date:
            if candidate.year == 2026:
                future_dates.append(candidate)
            candidate += datetime.timedelta(weeks=2)
        
        # Filtrar sólo los sábados donde el médico AÚN no está asignado
        already_global = {}
        if not df_s.empty:
            for fd in future_dates:
                docs_on_date = [dp.normalize_name_no_accents(n) for n in df_s[df_s['Date'] == fd]['Supernumerary'].tolist()]
                already_global[fd] = docs_on_date
        
        future_dates_to_add = [fd for fd in future_dates if new_doc and new_doc_norm not in already_global.get(fd, [])]
        
        if future_dates_to_add:
            with st.expander(f"📅 Secuencia automática: se replicará en {len(future_dates_to_add)} sábados", expanded=False):
                st.caption("El médico será agregado también a los siguientes sábados del ciclo:")
                cols_prev = st.columns(3)
                for i, fd in enumerate(future_dates_to_add):
                    cols_prev[i % 3].markdown(f"• **{fd.day} {MESES[fd.month-1]} {fd.year}**")
    
    if new_doc and new_doc_norm in already_assigned:
        st.warning(f"**{new_doc}** ya está asignado a este sábado ({sat_date.strftime('%d/%m/%Y')}). No se pueden tener duplicados.", icon=":material/warning:")
    
    if st.button("Agregar Médico", use_container_width=True, type="primary", icon=":material/person_add:"):
        if new_doc and new_doc_norm in already_assigned:
            st.error(f"No se puede agregar: **{new_doc}** ya está programado para este sábado.", icon=":material/error:")
        else:
            try:
                # GUARDAR ACCION EN LAST_ACTION PARA UNDO
                st.session_state.last_action = {
                    'action': 'AGREGAR',
                    'excel_path': st.session_state.excel_path,
                    'sheet': sheet,
                    'date': sat_date,
                    'doc': new_doc_norm,
                    'obs': obs.strip(),
                    'clasificacion': clasif
                }

                # Agrupar todas las inserciones (la actual y las replicadas) en un solo lote
                mods_batch = []
                
                # 1. Turno de la fecha actual seleccionada
                mods_batch.append({
                    'sheet': sheet,
                    'date': sat_date,
                    'doc': new_doc,
                    'obs': obs.strip(),
                    'clasificacion': clasif
                })

                # 2. Réplicas futuras de la secuencia
                if is_secuencia_normal and future_dates_to_add:
                    for fd in future_dates_to_add:
                        future_sheet = f"SABADOS {fd.year}"
                        if not df_s.empty and 'Date' in df_s.columns and 'Sheet' in df_s.columns:
                            rows_on_fd = df_s[df_s['Date'] == fd]
                            if not rows_on_fd.empty:
                                future_sheet = rows_on_fd.iloc[0]['Sheet']
                        mods_batch.append({
                            'sheet': future_sheet,
                            'date': fd,
                            'doc': new_doc,
                            'obs': '',  # sin obs en fechas replicadas
                            'clasificacion': clasif
                        })
                
                # Guardar todo el lote en una sola operación
                if mods_batch:
                    dp.add_shifts_batch(
                        excel_path=st.session_state.excel_path,
                        shifts_list=mods_batch
                    )
                    # Actualización optimista instantánea en memoria
                    new_rows = []
                    for m in mods_batch:
                        m_d = m['date']
                        m_d_norm = m_d if isinstance(m_d, datetime.date) and not isinstance(m_d, datetime.datetime) else (m_d.date() if isinstance(m_d, (datetime.datetime, pd.Timestamp)) else pd.to_datetime(m_d).date())
                        new_rows.append({
                            'Sheet': m['sheet'],
                            'Month_Header': dp.MONTH_NAMES_SP.get(m_d_norm.month if m_d_norm else 1, 'EXTRA'),
                            'Date': m_d_norm,
                            'Year': m_d_norm.year if m_d_norm else 2026,
                            'Month': m_d_norm.month if m_d_norm else 1,
                            'Supernumerary': str(m['doc']).strip().upper(),
                            'Excel_Row': 0,
                            'Excel_Col': 0,
                            'Header_Row': 0,
                            'Observation': str(m.get('obs', '')).strip(),
                            'Classification': str(m.get('clasificacion', 'Secuencia Normal')).strip()
                        })
                    if new_rows:
                        st.session_state.shifts_df = pd.concat([st.session_state.shifts_df, pd.DataFrame(new_rows)], ignore_index=True)
                        dp.load_modifications.clear()
                
                st.session_state["show_add_success_alert"] = True
                st.session_state["added_doc_name"] = new_doc
                st.session_state["add_alert_counter"] = st.session_state.get("add_alert_counter", 0) + 1
                
                st.rerun()
            except Exception as e:
                st.error(f"Error al agregar médico: {e}")

show_selection_dialog = show_shift_dialog


def es_misma_secuencia_sabado(d1, d2) -> bool:
    """
    Determina si dos sábados pertenecen a la misma secuencia quincenal.
    Retorna True si tienen la misma paridad quincenal (múltiplo de 14 días),
    lo cual significa que NO se pueden trasladar entre sí.
    Retorna False si pertenecen a secuencias contrarias (permitido).
    """
    if not d1 or not d2:
        return False
    try:
        if isinstance(d1, str):
            d1 = pd.to_datetime(d1).date()
        elif isinstance(d1, datetime.datetime):
            d1 = d1.date()

        if isinstance(d2, str):
            d2 = pd.to_datetime(d2).date()
        elif isinstance(d2, datetime.datetime):
            d2 = d2.date()

        diff_days = abs((d2 - d1).days)
        return (diff_days % 14) == 0
    except Exception:
        return False


def get_candidatos_intercambio(df_shifts: pd.DataFrame, target_date, doctor_to_exclude: str = "") -> list:
    """
    Retorna la lista ordenada de médicos disponibles para intercambio de turno en la fecha destino.
    Reglas de negocio estrictas:
    - Solo supernumerarios programados en la fecha destino (target_date).
    - EXCLUYE turnos por Compensación ('Compensación' en Classification).
    - EXCLUYE turnos por Cambio de turno ('Cambio' en Classification).
    - EXCLUYE al propio médico que se está trasladando (doctor_to_exclude).
    - Solo incluye los supernumerarios que pertenecen a la Secuencia Normal de ese sábado.
    """
    if df_shifts is None or not isinstance(df_shifts, pd.DataFrame) or df_shifts.empty or 'Date' not in df_shifts.columns:
        return []

    t_date = target_date
    if isinstance(t_date, str):
        try:
            t_date = pd.to_datetime(t_date).date()
        except Exception:
            pass
    elif isinstance(t_date, datetime.datetime):
        t_date = t_date.date()

    df_dates = pd.to_datetime(df_shifts['Date'], errors='coerce').dt.date
    target_shifts = df_shifts[df_dates == t_date].copy()

    if target_shifts.empty or 'Supernumerary' not in target_shifts.columns:
        return []

    # Filtrar estrictamente solo aquellos en Secuencia Normal (excluir Compensación y Cambio)
    if 'Classification' in target_shifts.columns:
        clasif_series = target_shifts['Classification'].astype(str)
        mask_secuencia_normal = (
            ~clasif_series.str.contains('Compensación', na=False, case=False) &
            ~clasif_series.str.contains('Cambio', na=False, case=False)
        )
        target_shifts = target_shifts[mask_secuencia_normal]

    doc_excl = str(doctor_to_exclude or "").strip().upper()
    candidatos = []
    for doc in target_shifts['Supernumerary'].dropna().unique():
        clean_d = str(doc).strip()
        if clean_d and clean_d.upper() != doc_excl:
            candidatos.append(clean_d)

    return sorted(candidatos)


@st.dialog("Modulo de turnos")
def show_drag_drop_action_dialog(payload, load_app_data_func):
    """
    Diálogo modal interactivo que se abre cuando un médico es arrastrado y soltado
    en otra columna de sábado.
    Permite elegir entre:
    1. Cambio de turno (intercambio mutuo con otro médico de secuencia contraria)
    2. Compensación de turno (traslado o turno adicional)
    3. Cambia de secuencia (reubicar el ciclo quincenal de sábados)
    """
    if not st.session_state.is_admin:
        st.error("Acceso denegado: Se requieren permisos de administrador.")
        st.stop()

    if not payload or not isinstance(payload, dict):
        st.session_state["active_drag_drop_payload"] = None
        st.rerun()

    doctor_name = str(payload.get('doctor', '')).strip().upper()
    source_date_raw = payload.get('source_date')
    target_date_raw = payload.get('target_date')

    if isinstance(source_date_raw, str):
        source_date = pd.to_datetime(source_date_raw).date()
    elif isinstance(source_date_raw, datetime.datetime):
        source_date = source_date_raw.date()
    else:
        source_date = source_date_raw

    if isinstance(target_date_raw, str):
        target_date = pd.to_datetime(target_date_raw).date()
    elif isinstance(target_date_raw, datetime.datetime):
        target_date = target_date_raw.date()
    else:
        target_date = target_date_raw

    source_str = f"{source_date.day} {dp.MONTH_NAMES_SP.get(source_date.month, '')} {source_date.year}" if source_date else str(source_date_raw)
    target_str = f"{target_date.day} {dp.MONTH_NAMES_SP.get(target_date.month, '')} {target_date.year}" if target_date else str(target_date_raw)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f0fbfb 0%, #e6f7f6 100%); border: 1.5px solid #0f9a9b; border-radius: 12px; padding: 12px 16px; margin-bottom: 14px;">
        <div style="font-size: 0.78rem; color: #5a7184; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Médico a Trasladar</div>
        <div style="font-size: 1.15rem; color: #17243D; font-weight: 800; font-family: Outfit, sans-serif; margin-bottom: 4px;">{doctor_name}</div>
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.88rem; color: #0f4c4c; font-weight: 600;">
            <span>📅 {source_str}</span>
            <span style="color: #0f9a9b; font-weight: 800; font-size: 1.1rem;">➔</span>
            <span>📅 {target_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    misma_secuencia = es_misma_secuencia_sabado(source_date, target_date)
    if misma_secuencia:
        st.error("⚠️ Restricción de secuencia: No es posible trasladar un médico a un sábado de su misma secuencia. Debe trasladarse a su secuencia contraria.")

    opciones_accion = [
        "Cambio de turno",
        "Compensación de turno",
        "Cambia de secuencia"
    ]
    accion_sel = st.radio("Acción a realizar:", opciones_accion, index=0)

    df_s = st.session_state.get('shifts_df', pd.DataFrame())
    excel_path = st.session_state.get('excel_path', '')

    # 1. OPCIÓN CAMBIO DE TURNO (Solo supernumerarios en su secuencia normal para ese sábado)
    swap_peer = None
    if accion_sel == "Cambio de turno":
        target_docs = get_candidatos_intercambio(df_s, target_date, doctor_name)

        if target_docs:
            swap_peer = st.selectbox("Seleccione el médico con quien intercambia turno:", target_docs)
        else:
            st.warning(f"No hay supernumerarios de secuencia normal programados el {target_str} disponibles para realizar el cambio.")
            swap_peer = None

        obs_val = st.text_input("Observaciones:", value="", key="dd_obs_cambio")

    # 2. OPCIÓN COMPENSACIÓN (Conserva el sábado actual y suma el turno de compensación en el sábado destino)
    elif accion_sel == "Compensación de turno":
        obs_val = st.text_input("Observaciones:", value="", key="dd_obs_comp")

    # 3. OPCIÓN CAMBIO DE SECUENCIA (Aplica automáticamente de ahí en adelante a todos los turnos futuros)
    else:
        obs_val = st.text_input("Observaciones:", value="", key="dd_obs_sec")

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns([1, 1])

    btn_disabled = bool(misma_secuencia or (accion_sel == "Cambio de turno" and not swap_peer))
    with c_btn1:
        if st.button("Confirmar y Aplicar", type="primary", use_container_width=True, key="btn_confirmar_drag_drop", disabled=btn_disabled):
            try:
                sheet_orig = payload.get('sheet') or f"SABADOS {source_date.year}"
                sheet_dest = f"SABADOS {target_date.year}"
                row_orig = int(payload.get('row', 0))
                col_orig = int(payload.get('col', 0))

                mods = []

                if accion_sel == "Cambio de turno":
                    # 1. CAMBIO DE TURNO (SWAP)
                    peer_match = df_s[(df_s['Date'] == target_date) & (df_s['Supernumerary'] == swap_peer)] if not df_s.empty else pd.DataFrame()
                    peer_row = int(peer_match.iloc[0]['Excel_Row']) if not peer_match.empty else 0
                    peer_col = int(peer_match.iloc[0]['Excel_Col']) if not peer_match.empty else 0
                    peer_sheet = str(peer_match.iloc[0]['Sheet']) if not peer_match.empty else sheet_dest

                    mods.append({
                        'sheet': sheet_orig,
                        'date': source_date,
                        'original_name': doctor_name,
                        'new_name': swap_peer,
                        'row': row_orig,
                        'col': col_orig,
                        'type': 'REEMPLAZAR',
                        'observaciones': obs_val.strip(),
                        'clasificacion': f"Cambio de turno con {swap_peer}"
                    })
                    mods.append({
                        'sheet': peer_sheet,
                        'date': target_date,
                        'original_name': swap_peer,
                        'new_name': doctor_name,
                        'row': peer_row,
                        'col': peer_col,
                        'type': 'REEMPLAZAR',
                        'observaciones': obs_val.strip(),
                        'clasificacion': f"Cambio de turno con {doctor_name}"
                    })

                    dp.save_modifications_batch(excel_path, mods)

                    df_upd = df_s.copy()
                    m_orig = (df_upd['Date'] == source_date) & (df_upd['Supernumerary'] == doctor_name)
                    m_dest = (df_upd['Date'] == target_date) & (df_upd['Supernumerary'] == swap_peer)
                    df_upd.loc[m_orig, 'Supernumerary'] = swap_peer
                    df_upd.loc[m_orig, 'Classification'] = f"Cambio de turno con {swap_peer}"
                    df_upd.loc[m_orig, 'Observation'] = obs_val.strip()
                    df_upd.loc[m_dest, 'Supernumerary'] = doctor_name
                    df_upd.loc[m_dest, 'Classification'] = f"Cambio de turno con {doctor_name}"
                    df_upd.loc[m_dest, 'Observation'] = obs_val.strip()
                    st.session_state.shifts_df = df_upd

                    st.session_state["show_swap_success_alert"] = True
                    st.session_state["swap_doc_1"] = doctor_name
                    st.session_state["swap_doc_2"] = swap_peer
                    st.session_state["swap_alert_counter"] = st.session_state.get("swap_alert_counter", 0) + 1

                elif accion_sel == "Compensación de turno":
                    # 2. COMPENSACIÓN: Conserva el turno en su sábado actual y se suma la compensación en el sábado destino
                    mods.append({
                        'sheet': sheet_dest,
                        'date': target_date,
                        'original_name': '',
                        'new_name': doctor_name,
                        'row': 0,
                        'col': 0,
                        'type': 'AGREGAR',
                        'observaciones': obs_val.strip(),
                        'clasificacion': 'Compensación / Pago de turno'
                    })

                    dp.save_modifications_batch(excel_path, mods)

                    df_upd = df_s.copy()
                    new_row = pd.DataFrame([{
                        'Sheet': sheet_dest,
                        'Month_Header': dp.MONTH_NAMES_SP.get(target_date.month, 'EXTRA'),
                        'Date': target_date,
                        'Year': target_date.year,
                        'Month': target_date.month,
                        'Supernumerary': doctor_name,
                        'Excel_Row': 0,
                        'Excel_Col': 0,
                        'Header_Row': 0,
                        'Observation': obs_val.strip(),
                        'Classification': 'Compensación / Pago de turno'
                    }])
                    st.session_state.shifts_df = pd.concat([df_upd, new_row], ignore_index=True)

                    st.session_state["show_edit_success_alert"] = True
                    st.session_state["edited_doc_name"] = f"{doctor_name} (Compensación)"
                    st.session_state["edit_alert_counter"] = st.session_state.get("edit_alert_counter", 0) + 1

                else:
                    # 3. CAMBIAR DE SECUENCIA (A partir de esta fecha en adelante: todos los turnos futuros)
                    source_parity = source_date.isocalendar()[1] % 2
                    day_shift = (target_date - source_date).days

                    futuros = df_s[
                        (df_s['Supernumerary'].astype(str).str.strip().str.upper() == doctor_name) &
                        (pd.to_datetime(df_s['Date']).dt.date >= source_date)
                    ]
                    
                    df_upd = df_s.copy()
                    for _, f_row in futuros.iterrows():
                        f_date = pd.to_datetime(f_row['Date']).date()
                        if (f_date.isocalendar()[1] % 2) == source_parity:
                            new_f_date = f_date + datetime.timedelta(days=day_shift)
                            mods.append({
                                'sheet': f_row['Sheet'],
                                'date': f_date,
                                'original_name': doctor_name,
                                'new_name': '',
                                'row': int(f_row.get('Excel_Row', 0)),
                                'col': int(f_row.get('Excel_Col', 0)),
                                'type': 'ELIMINAR',
                                'observaciones': '',
                                'clasificacion': f_row.get('Classification', 'Secuencia Normal')
                            })
                            mods.append({
                                'sheet': f"SABADOS {new_f_date.year}",
                                'date': new_f_date,
                                'original_name': '',
                                'new_name': doctor_name,
                                'row': 0,
                                'col': 0,
                                'type': 'AGREGAR',
                                'observaciones': obs_val.strip(),
                                'clasificacion': 'Secuencia Normal'
                            })
                            df_upd = df_upd.drop(index=df_upd[(df_upd['Date'] == f_date) & (df_upd['Supernumerary'] == doctor_name)].index)
                            df_upd = pd.concat([df_upd, pd.DataFrame([{
                                'Sheet': f"SABADOS {new_f_date.year}",
                                'Month_Header': dp.MONTH_NAMES_SP.get(new_f_date.month, 'EXTRA'),
                                'Date': new_f_date,
                                'Year': new_f_date.year,
                                'Month': new_f_date.month,
                                'Supernumerary': doctor_name,
                                'Excel_Row': 0,
                                'Excel_Col': 0,
                                'Header_Row': 0,
                                'Observation': obs_val.strip(),
                                'Classification': 'Secuencia Normal'
                            }])], ignore_index=True)
                    st.session_state.shifts_df = df_upd

                    if mods:
                        dp.save_modifications_batch(excel_path, mods)

                    st.session_state["show_edit_success_alert"] = True
                    st.session_state["edited_doc_name"] = f"{doctor_name} (Secuencia)"
                    st.session_state["edit_alert_counter"] = st.session_state.get("edit_alert_counter", 0) + 1

                dp.load_modifications.clear()
                st.session_state["active_drag_drop_payload"] = None
                st.rerun()
            except Exception as e:
                st.error(f"Error al aplicar la acción: {e}")

    with c_btn2:
        if st.button("Cancelar", type="secondary", use_container_width=True, key="btn_cancelar_drag_drop"):
            st.session_state["active_drag_drop_payload"] = None
            st.rerun()

