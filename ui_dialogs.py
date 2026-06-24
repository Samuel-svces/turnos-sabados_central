import streamlit as st
import datetime
import data_processor as dp

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
    st.markdown(f"### Opciones para el Sábado")
    st.write(f"**Médico:** {action_details['doctor']}")
    st.write(f"**Fecha:** {action_details['date'].strftime('%d/%m/%Y')}")
    st.markdown("---")
    
    col_change, col_delete = st.columns(2)
    with col_change:
        st.markdown("<div class='change-btn-wrapper'></div>", unsafe_allow_html=True)
        if st.button("Cambiar / Reemplazar", use_container_width=True):
            st.session_state.replacement_target = action_details
            st.rerun()
    with col_delete:
        if st.button("❌ Eliminar Asignación", use_container_width=True, type="primary"):
            try:
                # GUARDAR ACCION EN LAST_ACTION PARA UNDO
                st.session_state.last_action = {
                    'action': 'ELIMINAR',
                    'excel_path': st.session_state.excel_path,
                    'sheet': action_details['sheet'],
                    'row': action_details['row'],
                    'col': action_details['col'],
                    'date': action_details['date'],
                    'doc': action_details['doctor'],
                    'clasificacion': 'Secuencia Normal'
                }

                dp.delete_shift_cell(
                    excel_path=st.session_state.excel_path,
                    sheet_name=action_details['sheet'],
                    row_idx=action_details['row'],
                    col_idx=action_details['col'],
                    date_val=action_details['date'],
                    observation="",
                    original_name=action_details['doctor'],
                    clasificacion="Secuencia Normal"
                )
                st.success(f"Turno de {action_details['doctor']} eliminado.")
                load_app_data_func()
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")

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
