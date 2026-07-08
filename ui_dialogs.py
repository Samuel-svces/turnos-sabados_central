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

@st.dialog("Gestión de Turno")
def show_selection_dialog(action_details, load_app_data_func):
    if not st.session_state.is_admin:
        st.error("Acceso denegado: Se requieren permisos de administrador.")
        st.stop()
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
                    current_clasif
                )
            )
        with col_cancel:
            if st.button("↩️ Cancelar", use_container_width=True, key="btn_cancel_delete_action"):
                st.session_state.show_delete_options = False
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
                    current_doc
                )
            )

        with col_delete:
            if st.button("❌ Eliminar Asignación", use_container_width=True, type="secondary", key="btn_show_delete_options_action"):
                st.session_state.show_delete_options = True

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
