"""
cuadricula_turnos.py
--------------------
Componente de interfaz para la renderización de la cuadrícula de sábados.
Soporta:
  - Modo Administrador: Navegación de semanas, edición interactiva de turnos por modal,
    ordenamiento alfabético, adición de médicos y duplicación de programación anterior.
  - Modo Público: Visualización limpia de sólo lectura, filtrado por clasificación,
    indicadores de observación y tooltips detallados.
"""

import streamlit as st
import pandas as pd
import datetime
from modulos import procesador_datos as dp
from componentes import dialogos


def renderizar_cuadricula(df_shifts: pd.DataFrame, df_super: pd.DataFrame, search_query: str, cargar_datos_fn):
    """
    Renderiza la grilla de turnos de sábados completa según el modo de sesión (Admin o Público).
    """
    # Alertas de confirmación inyectadas desde el nivel superior
    if st.session_state.get("show_delete_success_alert", False):
        deleted_doc = st.session_state.get("deleted_doc_name", "Médico")
        st.components.v1.html(f"""
        <script>
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
                console.error("SweetAlert2 delete success injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_delete_success_alert"] = False

    if st.session_state.get("show_add_success_alert", False):
        added_doc = st.session_state.get("added_doc_name", "Médico")
        st.components.v1.html(f"""
        <script>
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
        return

    if st.session_state.is_admin:
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
            if st.button("◀ Sábados Anteriores", use_container_width=True, disabled=not has_prev, key="btn_admin_sats_anteriores"):
                st.session_state.saturday_offset = max(0, offset - 4)
                st.rerun()
        with col_nav_info:
            start_sat = offset + 1
            end_sat = min(len(all_visible_saturdays), offset + 4)
            st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 0.5rem; color: #1565c0; font-family: Outfit; font-size: 1.05rem;'>Sábados {start_sat} a {end_sat} de {len(all_visible_saturdays)} programados</div>", unsafe_allow_html=True)
        with col_nav_next:
            has_next = offset + 4 < len(all_visible_saturdays)
            if st.button("Siguientes Sábados ▶", use_container_width=True, disabled=not has_next, key="btn_admin_sats_siguientes"):
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
        # VISTA ADMINISTRADOR: Botones interactivos con diálogo de edición
        st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
        st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
        cols = st.columns(len(saturdays))
        for idx, sat_date in enumerate(saturdays):
            with cols[idx]:
                st.markdown("<div class='saturday-col-marker'></div>", unsafe_allow_html=True)
                is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                
                date_shifts_all = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                num_doctors_all = len(date_shifts_all)
                doc_counts = date_shifts_all['Supernumerary'].value_counts() if not date_shifts_all.empty else pd.Series()
                
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
                if st.button(header_text, key=f"btn_ordenar_admin_{sat_date}", use_container_width=True):
                    st.session_state.column_sorts[sat_date] = "natural" if sort_type == "asc" else "asc"
                    st.rerun()
                
                # Lista de médicos como botones interactivos
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
                    
                    display_name = name
                    if has_conflict:
                        display_name += " 🚨(DUPLICADO)"
                    if "Compensación" in str(clasif):
                        display_name += " 🟡(COMP)"
                    elif "Cambio" in str(clasif):
                        display_name += f" 🔄({clasif.split(' con ')[0]})"
                        
                    if search_query and search_query in name.upper():
                        display_name = "🎯 " + display_name
                        
                    if shift_obs or personal_obs:
                        display_name += " 💬"
                        
                    help_lines = []
                    if "Compensación" in str(clasif): help_lines.append("⚠️ Turno de compensación")
                    if clasif and clasif != "Secuencia Normal": help_lines.append(f"ℹ️ {clasif}")
                    if shift_obs: help_lines.append(f"💬 {shift_obs}")
                    if personal_obs: help_lines.append(f"👤 {personal_obs}")
                    
                    help_text = "\n".join(help_lines).strip()
                    
                    if st.button(display_name, key=f"btn_turno_admin_{sat_date}_{s_idx}", use_container_width=True, help=help_text if help_text else None):
                        action_details = {
                            'date': sat_date,
                            'doctor': name,
                            'row': int(s_row['Excel_Row']),
                            'col': int(s_row['Excel_Col']),
                            'sheet': s_row['Sheet'],
                            'observation': shift_obs,
                            'classification': clasif
                        }
                        dialogos.show_shift_dialog(action_details, cargar_datos_fn)
                    
                st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
                
                # 1. Botón Agregar Médico
                sheet_name = date_shifts_all.iloc[0]['Sheet'] if not date_shifts_all.empty else f"SABADOS {sat_date.year}"
                if st.button("Agregar Médico", key=f"btn_agregar_medico_{sat_date}", use_container_width=True, type="primary", icon=":material/person_add:"):
                    dialogos.show_add_dialog(sat_date, sheet_name, cargar_datos_fn)
                    
                # 2. Botón Duplicar (si existen turnos anteriores)
                two_weeks_ago = sat_date - datetime.timedelta(weeks=2)
                prev_shifts = df_shifts[df_shifts['Date'] == two_weeks_ago] if not df_shifts.empty else pd.DataFrame()
                if not prev_shifts.empty:
                    st.markdown("<div class='dup-btn-wrapper'></div>", unsafe_allow_html=True)
                    label_dup = f"Duplicar del {two_weeks_ago.day} {dp.MONTH_NAMES_SP[two_weeks_ago.month]}"
                    if st.button(label_dup, key=f"btn_duplicar_{sat_date}", use_container_width=True):
                        with st.spinner("Duplicando..."):
                            try:
                                target_sheet = date_shifts_all.iloc[0]['Sheet'] if not date_shifts_all.empty else f"SABADOS {sat_date.year}"
                                
                                shifts_to_delete_list = []
                                if not date_shifts_all.empty:
                                    for _, row_to_del in date_shifts_all.iterrows():
                                        clasif_dest = str(row_to_del.get('Classification', 'Secuencia Normal'))
                                        if "Compensación" in clasif_dest or "Cambio" in clasif_dest:
                                            continue
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
                                        continue
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
                                cargar_datos_fn()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al duplicar: {e}")
                                
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # VISTA PÚBLICA: Cuadrícula limpia de solo lectura
        with st.container():
            st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
            st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
            cols = st.columns(len(saturdays))
            for idx, sat_date in enumerate(saturdays):
                with cols[idx]:
                    st.markdown("<div class='saturday-col-marker'></div>", unsafe_allow_html=True)
                    is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                    
                    date_shifts_all = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                    num_doctors_all = len(date_shifts_all)
                    
                    date_shifts = date_shifts_all.copy()
                    filter_val = st.session_state.get("filter_class", "Todos")
                    if filter_val != "Todos":
                        date_shifts = date_shifts[date_shifts['Classification'].str.contains(filter_val, na=False, case=False)]
                    
                    num_doctors_filtered = len(date_shifts)
                    
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
                    if st.button(header_text, key=f"btn_ordenar_pub_{sat_date}", use_container_width=True):
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
                        
                        display_name = name
                        if "Cambio" in str(clasif):
                            display_name += f" ({clasif})"
                        
                        st.markdown(f"<div class='doc-btn-wrap'><div class='{badge_classes}'>{obs_dot}{display_name}</div>{tooltip_html}</div>", unsafe_allow_html=True)
                        
            st.markdown("</div>", unsafe_allow_html=True)
