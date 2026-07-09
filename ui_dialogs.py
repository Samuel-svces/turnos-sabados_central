import streamlit as st
import datetime
import data_processor as dp
import pandas as pd

def get_allowed_doctors():
    df_s = st.session_state.shifts_df
    df_sup = st.session_state.super_df
    june_date = datetime.date(2026, 6, 1)
    docs_with_shifts = df_s[df_s['Date'] >= june_date]['Supernumerary'].unique().tolist()
    
    try:
        df_pm = dp.load_personal_modifications(st.session_state.excel_path)
        added_docs = df_pm[df_pm['TYPE'] == 'AGREGAR']['NOMBRES_Y_APELLIDOS'].unique().tolist()
    except Exception:
        added_docs = []
        
    if not df_sup.empty:
        allowed = df_sup[df_sup['NOMBRES Y APELLIDOS'].isin(docs_with_shifts + added_docs)]['NOMBRES Y APELLIDOS'].tolist()
        allowed = sorted(list(set(allowed + docs_with_shifts + added_docs)))
    else:
        allowed = sorted(list(set(docs_with_shifts + added_docs)))
    return allowed

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
            old_counterpart = current_clasif.replace("Cambio de turno con ", "").strip()
            df_s = st.session_state.shifts_df
            df_s_dates = pd.to_datetime(df_s['Date'], errors='coerce').dt.date
            match_counterpart = df_s[(df_s['Supernumerary'] == old_counterpart) & 
                                     (df_s['Classification'].str.contains(current_doc, na=False)) &
                                     (df_s_dates == date_check)]
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
            # Guardar médico de origen
            mods_list.append({
                'sheet': sheet,
                'date': date_val,
                'original_name': current_doc,
                'new_name': current_doc,
                'row': row,
                'col': col,
                'type': 'REEMPLAZAR',
                'observaciones': observation.strip(),
                'clasificacion': f"Cambio de turno con {swap_target['doctor']}"
            })
            
            # Guardar médico de destino
            mods_list.append({
                'sheet': swap_target['sheet'],
                'date': swap_target['date'],
                'original_name': swap_target['doctor'],
                'new_name': swap_target['doctor'],
                'row': swap_target['row'],
                'col': swap_target['col'],
                'type': 'REEMPLAZAR',
                'observaciones': swap_target['observation'],
                'clasificacion': f"Cambio de turno con {current_doc}"
            })
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
            
        if mods_list:
            dp.save_modifications_batch(excel_path, mods_list)
            
        st.session_state.show_delete_options = False
        st.session_state.should_rerun_main = True
        load_app_data_func()
        st.rerun()
    except Exception as e:
        st.session_state.last_error = f"Error al guardar cambios: {e}"
        st.rerun()

def delete_shift_callback(excel_path, sheet, row, col, date_val, current_doc, current_clasif, load_app_data_func):
    try:
        df_s = st.session_state.shifts_df
        del_scope = st.session_state.get("del_scope_radio_flat", "Eliminar solo de esta secuencia")
        
        # Asegurarnos de que date_val sea datetime.date
        date_check = date_val
        if isinstance(date_check, datetime.datetime):
            date_check = date_check.date()
        elif isinstance(date_check, str):
            date_check = pd.to_datetime(date_check).date()

        # Convertir a datetime.date para comparación segura
        df_s_dates = pd.to_datetime(df_s['Date'], errors='coerce').dt.date

        if del_scope == "Eliminar de todas las secuencias (las futuras)":
            shifts_to_delete = df_s[
                (df_s['Supernumerary'] == current_doc) & 
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

            if shifts_to_delete.empty:
                shifts_to_delete = df_s[
                    (df_s['Sheet'] == sheet) &
                    (df_s_dates == date_check) &
                    (df_s['Supernumerary'] == current_doc)
                ]
        
        if shifts_to_delete.empty:
            st.session_state.last_error = "No se encontraron asignaciones coincidentes para eliminar."
            st.rerun()
        else:
            deleted_count = 0
            deleted_items_log = []
            mods_list = []
            
            for _, r_del in shifts_to_delete.iterrows():
                row_clasif = r_del.get('Classification', 'Secuencia Normal')
                
                # Limpiar contraparte si era un cambio de turno
                if "Cambio de turno con" in row_clasif:
                    old_counterpart = row_clasif.replace("Cambio de turno con ", "").strip()
                    r_del_date = r_del['Date']
                    if isinstance(r_del_date, datetime.datetime):
                        r_del_date = r_del_date.date()
                    elif isinstance(r_del_date, str):
                        r_del_date = pd.to_datetime(r_del_date).date()

                    match_counterpart = df_s[
                        (df_s['Supernumerary'] == old_counterpart) & 
                        (df_s['Classification'].str.contains(r_del['Supernumerary'], na=False)) &
                        (df_s_dates == r_del_date)
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
            st.session_state["show_delete_success_alert"] = True
            st.session_state["deleted_doc_name"] = current_doc
            load_app_data_func()
            # No llamamos st.rerun() aquí: on_click ya dispara el rerun automáticamente
    except Exception as e:
        st.session_state.last_error = f"Error al eliminar: {e}"

def show_delete_options_callback():
    st.session_state.show_delete_options = True

def cancel_delete_options_callback():
    st.session_state.show_delete_options = False
    st.session_state.last_error = None

@st.dialog("Gestión de Turno")
def show_selection_dialog(action_details, load_app_data_func):
    if not st.session_state.is_admin:
        st.error("Acceso denegado: Se requieren permisos de administrador.")
        st.stop()

    # Inyectar SweetAlert de éxito si viene de una eliminación
    # Lo hacemos aquí (dentro del dialog) usando window.parent para alcanzar la ventana principal
    if st.session_state.get("show_delete_success_alert", False):
        deleted_doc = st.session_state.get("deleted_doc_name", "Médico")
        st.components.v1.html(f"""
        <script>
            // Disparar SweetAlert luego de que el dialog se cierre
            const showDeleteAlert = () => {{
                window.parent.Swal.fire({{
                    title: "Usuario Eliminado",
                    text: "{deleted_doc} fue eliminado correctamente.",
                    icon: "success",
                    draggable: true,
                    confirmButtonColor: '#1a73e8',
                    timer: 3500,
                    timerProgressBar: true
                }});
            }};
            if (window.parent.Swal) {{
                setTimeout(showDeleteAlert, 300);
            }} else {{
                const s = window.parent.document.createElement('script');
                s.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                s.onload = () => setTimeout(showDeleteAlert, 300);
                window.parent.document.head.appendChild(s);
            }}
        </script>
        """, height=0)
        st.session_state["show_delete_success_alert"] = False

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
    
    allowed = get_allowed_doctors()
    current_doc = action_details['doctor']
    if current_doc not in allowed:
        allowed = sorted(list(set(allowed + [current_doc])))
    try:
        default_idx = allowed.index(current_doc)
    except ValueError:
        default_idx = 0
        
    new_doc = st.selectbox("Médico Programado:", allowed, index=default_idx, disabled=True)
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
        st.markdown("##### 🗑️ Confirmar Eliminación de Asignación")
        
        del_scope = st.radio(
            "Seleccione una opción para eliminar:",
            ["Eliminar solo de esta secuencia", "Eliminar de todas las secuencias (las futuras)"],
            index=0,
            key="del_scope_radio_flat"
        )
        
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            st.button(
                "Confirmar", 
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
        col_save, col_delete = st.columns(2)
        
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
                "Eliminar Asignación", 
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
    already_assigned = [n.upper() for n in df_s[df_s['Date'] == sat_date]['Supernumerary'].tolist()]
    
    allowed = get_allowed_doctors()
    new_doc = st.selectbox("Seleccione Médico Supernumerario:", allowed)
    obs = st.text_input("Observaciones (opcional):", placeholder="Ej: Pago de turno...")
    clasif = st.radio("Clasificación del Turno:", ["Secuencia Normal", "Compensación / Pago de turno"], horizontal=True)
    
    # Calcular sábados futuros del mismo ciclo biemanal (cada 14 días)
    is_secuencia_normal = (clasif == "Secuencia Normal")
    future_dates = []
    if is_secuencia_normal:
        candidate = sat_date + datetime.timedelta(weeks=2)
        end_date = sat_date + datetime.timedelta(weeks=52)
        while candidate <= end_date:
            future_dates.append(candidate)
            candidate += datetime.timedelta(weeks=2)
        
        # Filtrar sólo los sábados donde el médico AÚN no está asignado
        already_global = {}
        if not df_s.empty:
            for fd in future_dates:
                docs_on_date = [n.upper() for n in df_s[df_s['Date'] == fd]['Supernumerary'].tolist()]
                already_global[fd] = docs_on_date
        
        future_dates_to_add = [fd for fd in future_dates if new_doc and new_doc.upper() not in already_global.get(fd, [])]
        
        if future_dates_to_add:
            with st.expander(f"📅 Secuencia automática: se replicará en {len(future_dates_to_add)} sábados", expanded=False):
                st.caption("El médico será agregado también a los siguientes sábados del ciclo:")
                cols_prev = st.columns(3)
                for i, fd in enumerate(future_dates_to_add):
                    cols_prev[i % 3].markdown(f"• **{fd.day} {MESES[fd.month-1]} {fd.year}**")
    
    if new_doc and new_doc.upper() in already_assigned:
        st.warning(f"⚠️ **{new_doc}** ya está asignado a este sábado ({sat_date.strftime('%d/%m/%Y')}). No se pueden tener duplicados.")
    
    if st.button("Agregar Médico", use_container_width=True, type="primary", icon=":material/person_add:"):
        if new_doc and new_doc.upper() in already_assigned:
            st.error(f"No se puede agregar: **{new_doc}** ya está programado para este sábado.")
        else:
            try:
                # GUARDAR ACCION EN LAST_ACTION PARA UNDO
                st.session_state.last_action = {
                    'action': 'AGREGAR',
                    'excel_path': st.session_state.excel_path,
                    'sheet': sheet,
                    'date': sat_date,
                    'doc': new_doc,
                    'obs': obs.strip(),
                    'clasificacion': clasif
                }

                # Agregar en la fecha seleccionada
                dp.add_shift_to_date(
                    excel_path=st.session_state.excel_path,
                    sheet_name=sheet,
                    target_date=sat_date,
                    supernumerary_name=new_doc,
                    observation=obs.strip(),
                    clasificacion=clasif
                )

                # Si es Secuencia Normal, replicar en el ciclo biemanal hacia adelante
                if is_secuencia_normal and future_dates_to_add:
                    # Determinar el sheet de cada fecha futura (por año)
                    mods_batch = []
                    for fd in future_dates_to_add:
                        future_sheet = f"SABADOS {fd.year}"
                        # Si existe un sheet conocido en df_s para esa fecha, usarlo
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
                    if mods_batch:
                        dp.add_shifts_batch(
                            excel_path=st.session_state.excel_path,
                            shifts_list=mods_batch
                        )
                    total = 1 + len(future_dates_to_add)
                    st.success(f"✅ {new_doc} agregado con éxito en **{total} sábados** (fecha actual + {len(future_dates_to_add)} del ciclo biemanal).")
                else:
                    st.success(f"Médico {new_doc} agregado con éxito.")

                load_app_data_func()
                st.rerun()
            except Exception as e:
                st.error(f"Error al agregar médico: {e}")

