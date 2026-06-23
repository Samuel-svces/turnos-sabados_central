import codecs

with codecs.open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out_lines = []
skip = False
i = 0
while i < len(lines):
    line = lines[i]
    
    # Replace tabs logic
    if '# Navigation Tabs' in line:
        out_lines.append('# Navigation Tabs\n')
        out_lines.append('tabs_list = ["Calendario de Turnos"]\n')
        out_lines.append('if st.session_state.is_admin:\n')
        out_lines.append('    tabs_list.extend(["Directorio y Sincronización"])\n\n')
        out_lines.append('tabs = st.tabs(tabs_list)\n')
        out_lines.append('tab_calendar = tabs[0]\n')
        out_lines.append('if st.session_state.is_admin:\n')
        out_lines.append('    tab_admin = tabs[1]\n')
        i += 11 # skip original 11 lines up to tab_admin = tabs[2]
        continue
        
    # Replace notification logic
    if 'with col_notif:' in line:
        new_notif = '''with col_notif:
    if st.session_state.is_admin:
        df_req_local = st.session_state.req_df if 'req_df' in st.session_state else pd.DataFrame()
        pending_count = 0
        if not df_req_local.empty and 'ESTADO' in df_req_local.columns:
            pending_count = len(df_req_local[df_req_local['ESTADO'] == 'PENDIENTE'])
            
        notif_label = f"🔔 {pending_count}" if pending_count > 0 else "🔔"
        notif_help = f"{pending_count} solicitudes pendientes" if pending_count > 0 else "Buzón de Solicitudes"
        
        with st.popover(notif_label, help=notif_help, use_container_width=True):
            st.markdown("### <i class='bi bi-bell-fill'></i> Buzón de Solicitudes", unsafe_allow_html=True)
            st.markdown("---")
            
            tab_p, tab_h = st.tabs(["Pendientes", "Historial"])
            
            with tab_p:
                if pending_count == 0:
                    st.info("No hay solicitudes pendientes.")
                else:
                    st.write(f"Tienes **{pending_count}** solicitudes por revisar:")
                    pending_reqs = df_req_local[df_req_local['ESTADO'] == 'PENDIENTE']
                    for _, r_row in pending_reqs.iterrows():
                        r_id = r_row['ID']
                        orig = r_row['MEDICO_ORIGINAL']
                        reemp = r_row['MEDICO_REEMPLAZO']
                        t_date = r_row['FECHA_TURNO']
                        motivo = r_row['MOTIVO']
                        date_str = t_date.strftime('%d/%m/%Y') if hasattr(t_date, 'strftime') else str(t_date)
                        
                        st.markdown(
                            f"""
                            <div style='padding: 0.75rem; background-color: #f8f9fa; border-left: 4px solid #1a73e8; border-radius: 6px; margin-bottom: 0.5rem;'>
                                <b>Solicitud #{r_id}</b><br/>
                                👤 <b>Original:</b> {orig}<br/>
                                🔄 <b>Reemplazo:</b> {reemp}<br/>
                                📅 <b>Fecha:</b> {date_str}<br/>
                                💡 <b>Motivo:</b> {motivo}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        notes_key = f"notif_notes_{r_id}"
                        notes_input = st.text_input("Notas de Decisión:", key=notes_key, placeholder="Ej: Aprobado...", label_visibility="collapsed")
                        
                        col_app, col_rej = st.columns(2)
                        with col_app:
                            if st.button("Aprobar", key=f"notif_appr_{r_id}", use_container_width=True, type="primary"):
                                try:
                                    dp.resolve_change_request(st.session_state.excel_path, r_id, 'APROBADO', notes_input)
                                    load_app_data()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        with col_rej:
                            if st.button("Rechazar", key=f"notif_rej_{r_id}", use_container_width=True):
                                try:
                                    dp.resolve_change_request(st.session_state.excel_path, r_id, 'RECHAZADO', notes_input)
                                    load_app_data()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        st.markdown("<hr style='margin: 0.5rem 0;' />", unsafe_allow_html=True)
            
            with tab_h:
                if df_req_local.empty:
                    st.info("No hay historial.")
                else:
                    hist_reqs = df_req_local[df_req_local['ESTADO'] != 'PENDIENTE'].sort_values('ID', ascending=False)
                    if hist_reqs.empty:
                        st.info("No hay historial de solicitudes resueltas.")
                    else:
                        for _, r_row in hist_reqs.iterrows():
                            r_id = r_row['ID']
                            orig = r_row['MEDICO_ORIGINAL']
                            reemp = r_row['MEDICO_REEMPLAZO']
                            t_date = r_row['FECHA_TURNO']
                            state = r_row['ESTADO']
                            motivo = r_row['MOTIVO']
                            resol_date = r_row['FECHA_RESOLUCION']
                            obs = r_row['OBSERVACIONES']
                            
                            date_str = t_date.strftime('%d/%m/%Y') if hasattr(t_date, 'strftime') else str(t_date)
                            badge_color = "#4caf50" if state == "APROBADO" else "#f44336"
                            
                            with st.expander(f"#{r_id} | {state} | {orig.split()[0]} -> {reemp.split()[0]}"):
                                st.markdown(f"**Estado:** <span style='color: {badge_color}; font-weight: bold;'>{state}</span>", unsafe_allow_html=True)
                                st.write(f"**Fecha Turno:** {date_str}")
                                st.write(f"**Original:** {orig}")
                                st.write(f"**Reemplazo:** {reemp}")
                                st.write(f"**Motivo:** {motivo}")
                                if pd.notna(resol_date):
                                    st.write(f"**Decisión el:** {resol_date.strftime('%d/%m/%Y')}")
                                if obs:
                                    st.write(f"**Notas:** {obs}")
'''
        out_lines.append(new_notif)
        
        # skip lines until the next block
        while i < len(lines) and 'if not st.session_state.data_loaded or st.session_state.load_error:' not in lines[i]:
            i += 1
        continue
        
    # Remove NON-ADMIN INBOX and TAB 2
    if '# ----------------- NON-ADMIN INBOX IN TAB 1 -----------------' in line:
        while i < len(lines) and '# ----------------- TAB 3: ADMIN CONTROL PANEL -----------------' not in lines[i]:
            i += 1
        continue
        
    out_lines.append(line)
    i += 1

with codecs.open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(out_lines)
print('Done!')
