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

        # 1. Limpiar contraparte anterior si esta asignación ya tenía un cambio registrado
        if "Cambio de turno con" in current_clasif:
            old_counterpart = current_clasif.replace("Cambio de turno con ", "").strip()
            df_s = st.session_state.shifts_df
            df_s_dates = pd.to_datetime(df_s['Date'], errors='coerce').dt.date
            match_counterpart = df_s[(df_s['Supernumerary'] == old_counterpart) & 
                                     (df_s['Classification'].str.contains(current_doc, na=False)) &
                                     (df_s_dates == date_check)]
            for _, r_match in match_counterpart.iterrows():
                dp.update_shift_cell(
                    excel_path=excel_path,
                    sheet_name=r_match['Sheet'],
                    row_idx=int(r_match['Excel_Row']),
                    col_idx=int(r_match['Excel_Col']),
                    new_name=r_match['Supernumerary'],
                    date_val=r_match['Date'],
                    observation=r_match.get('Observation', ''),
                    original_name=r_match['Supernumerary'],
                    clasificacion="Secuencia Normal"
                )
        
        # 2. Guardar cambios del turno
        if classification == "Cambio de turno" and swap_target:
            # Guardar médico de origen
            dp.update_shift_cell(
                excel_path=excel_path,
                sheet_name=sheet,
                row_idx=row,
                col_idx=col,
                new_name=current_doc,
                date_val=date_val,
                observation=observation.strip(),
                original_name=current_doc,
                clasificacion=f"Cambio de turno con {swap_target['doctor']}"
            )
            
            # Guardar médico de destino
            dp.update_shift_cell(
                excel_path=excel_path,
                sheet_name=swap_target['sheet'],
                row_idx=swap_target['row'],
                col_idx=swap_target['col'],
                new_name=swap_target['doctor'],
                date_val=swap_target['date'],
                observation=swap_target['observation'],
                original_name=swap_target['doctor'],
                clasificacion=f"Cambio de turno con {current_doc}"
            )
        else:
            dp.update_shift_cell(
                excel_path=excel_path,
                sheet_name=sheet,
                row_idx=row,
                col_idx=col,
                new_name=new_name,
                date_val=date_val,
                observation=observation.strip(),
                original_name=original_name,
                clasificacion=classification
            )
            
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
                        dp.update_shift_cell(
                            excel_path=excel_path,
                            sheet_name=cp_row['Sheet'],
                            row_idx=int(cp_row['Excel_Row']),
                            col_idx=int(cp_row['Excel_Col']),
                            new_name=cp_row['Supernumerary'],
                            date_val=cp_row['Date'],
                            observation=cp_row.get('Observation', ''),
                            original_name=cp_row['Supernumerary'],
                            clasificacion="Secuencia Normal"
                        )
                
                # Guardar log para deshacer
                deleted_items_log.append({
                    'sheet': r_del['Sheet'], 'date': r_del['Date'], 'doc': r_del['Supernumerary'],
                    'obs': r_del.get('Observation', ''), 'clasificacion': row_clasif
                })
                
                # Eliminar el turno
                dp.delete_shift_cell(
                    excel_path=excel_path,
                    sheet_name=r_del['Sheet'],
                    row_idx=int(r_del['Excel_Row']),
                    col_idx=int(r_del['Excel_Col']),
                    date_val=r_del['Date'],
                    observation="",
                    original_name=r_del['Supernumerary'],
                    clasificacion=row_clasif
                )
                deleted_count += 1
            
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
            load_app_data_func()
            st.rerun()
    except Exception as e:
        st.session_state.last_error = f"Error al eliminar: {e}"
        st.rerun()

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
            other_docs = sorted(other_docs)
            
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
                "❌ Confirmar", 
                use_container_width=True, 
                type="primary", 
                key="btn_confirm_delete_action",
                on_click=delete_shift_callback,
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
                "↩️ Cancelar", 
                use_container_width=True, 
                key="btn_cancel_delete_action",
                on_click=cancel_delete_options_callback
            )
    else:
        col_save, col_delete = st.columns(2)
        
        with col_save:
            st.button(
                "💾 Guardar Cambios", 
                use_container_width=True, 
                type="primary", 
                key="btn_save_changes_action",
                on_click=save_changes_callback,
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
                "❌ Eliminar Asignación", 
                use_container_width=True, 
                type="secondary", 
                key="btn_show_delete_options_action",
                on_click=show_delete_options_callback
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
    
    if new_doc and new_doc.upper() in already_assigned:
        st.warning(f"⚠️ **{new_doc}** ya está asignado a este sábado ({sat_date.strftime('%d/%m/%Y')}). No se pueden tener duplicados.")
    
    if st.button("Agregar Médico", use_container_width=True, type="primary"):
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

                dp.add_shift_to_date(
                    excel_path=st.session_state.excel_path,
                    sheet_name=sheet,
                    target_date=sat_date,
                    supernumerary_name=new_doc,
                    observation=obs.strip(),
                    clasificacion=clasif
                )
                st.success(f"Médico {new_doc} agregado con éxito.")
                load_app_data_func()
                st.rerun()
            except Exception as e:
                st.error(f"Error al agregar médico: {e}")
