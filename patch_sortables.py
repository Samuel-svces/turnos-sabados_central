import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if 'tab_calendar = tabs[0]' in line:
        start_idx = i
        break

end_idx = -1
for i, line in enumerate(lines):
    if 'TAB 3: ADMIN CONTROL PANEL' in line:
        end_idx = i
        break

new_calendar_code = """from streamlit_sortables import sort_items

with tab_calendar:
    st.markdown("### <i class='bi bi-calendar3'></i> Programación Mensual de Sábados", unsafe_allow_html=True)
    
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
            for sat_date in saturdays:
                date_shifts = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                
                header_text = sat_date.strftime('%d de %b, %Y').upper()
                is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                if is_holiday:
                    header_text += " (FESTIVO)"
                    
                docs = [row['Supernumerary'] for _, row in date_shifts.iterrows()]
                
                original_state.append({
                    'header': header_text,
                    'items': docs,
                    'date': sat_date.strftime('%Y-%m-%d')
                })
                
            # Render sortable columns
            returned_state = sort_items(
                [{'header': c['header'], 'items': c['items']} for c in original_state],
                multi_containers=True,
                direction='horizontal',
                key="sortable_sats"
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
                        old_row = df_shifts[(df_shifts['Date'] == old_date) & (df_shifts['Supernumerary'] == moved_doc)].iloc[0]
                        sheet = old_row['Sheet']
                        r_idx = int(old_row['Excel_Row'])
                        c_idx = int(old_row['Excel_Col'])
                        obs = str(old_row.get('Observation', '')) if pd.notna(old_row.get('Observation')) else ''
                        clasif = old_row.get('Classification', 'Secuencia Normal')
                        
                        # 2. Check if the doc is already in the new date (duplicate)
                        new_date_shifts = month_shifts[month_shifts['Date'] == new_date]
                        if not new_date_shifts.empty and moved_doc in new_date_shifts['Supernumerary'].values:
                            st.error(f"¡El médico {moved_doc} ya tiene un turno el {to_date}! Movimiento cancelado.")
                            st.rerun()
                            
                        # 3. Delete old
                        dp.delete_shift_cell(
                            excel_path=st.session_state.excel_path,
                            sheet_name=sheet,
                            row_idx=r_idx,
                            col_idx=c_idx,
                            date_val=old_date,
                            observation="",
                            original_name=moved_doc,
                            clasificacion="Secuencia Normal"
                        )
                        
                        # 4. Add new
                        target_sheet = sheet
                        dp.add_shift_to_date(
                            excel_path=st.session_state.excel_path,
                            sheet_name=target_sheet,
                            target_date=new_date,
                            supernumerary_name=moved_doc,
                            observation=obs,
                            clasificacion=clasif
                        )
                        
                        st.success(f"✅ ¡Turno de {moved_doc} movido exitosamente al {to_date}!")
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
                        for _, s_row in date_shifts.reset_index().iterrows():
                            name = s_row['Supernumerary']
                            if st.button(f"Editar {name}", key=f"edit_btn_{sat_date}_{name}"):
                                action_details = {
                                    'date': sat_date,
                                    'doctor': name,
                                    'row': int(s_row['Excel_Row']),
                                    'col': int(s_row['Excel_Col']),
                                    'sheet': s_row['Sheet']
                                }
                                show_selection_dialog(action_details)
                                
                        if st.button("➕ Agregar Médico", key=f"add_btn_{sat_date}", use_container_width=True):
                            sheet_name = date_shifts.iloc[0]['Sheet'] if not date_shifts.empty else f"SABADOS {sat_date.year}"
                            show_add_dialog(sat_date, sheet_name)

        else:
            # PUBLIC VIEW: Read-Only Grid
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
                        obs_dot = "<span class='obs-dot'></span>" if has_obs else ""
                        tooltip_html = f"<div class='doc-obs-tooltip'>{help_text}</div>" if help_text else ""
                        
                        st.markdown(f"<div class='doc-btn-wrap'><div class='{badge_classes}'>{obs_dot}{name}</div>{tooltip_html}</div>", unsafe_allow_html=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

"""

final_lines = lines[:start_idx + 1] + [new_calendar_code + '\n'] + lines[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print('Sortables logic inserted successfully.')
