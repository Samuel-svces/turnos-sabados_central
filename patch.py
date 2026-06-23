import os
import datetime
import pandas as pd

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

new_calendar_code = """from streamlit_calendar import calendar

with tab_calendar:
    st.markdown("### <i class='bi bi-calendar3'></i> Programación Mensual de Sábados", unsafe_allow_html=True)
    
    events = []
    if not df_shifts.empty and 'Date' in df_shifts.columns:
        for idx, row in df_shifts.iterrows():
            name = row['Supernumerary']
            d = row['Date']
            obs = str(row.get('Observation', '')) if pd.notna(row.get('Observation')) else ''
            clasif = row.get('Classification', 'Secuencia Normal')
            
            personal_obs = ""
            if not df_super.empty:
                doc_match = df_super[df_super['NOMBRES Y APELLIDOS'] == name]
                if not doc_match.empty:
                    personal_obs = str(doc_match.iloc[0].get('OBSERVACIONES', '')).strip()
            
            bg_color = "#e8f0fe"
            text_color = "#1a73e8"
            if "Compensación" in str(clasif):
                bg_color = "#ffe0b2"
                text_color = "#e65100"
            
            tooltip = f"{clasif}"
            if obs: tooltip += f" | {obs}"
            if personal_obs: tooltip += f" | {personal_obs}"
                
            events.append({
                "id": f"{row['Sheet']}|{row['Excel_Row']}|{row['Excel_Col']}|{name}|{d.strftime('%Y-%m-%d')}",
                "title": name,
                "start": d.strftime("%Y-%m-%d"),
                "allDay": True,
                "backgroundColor": bg_color,
                "textColor": text_color,
                "extendedProps": {
                    "sheet": row['Sheet'],
                    "row": int(row['Excel_Row']),
                    "col": int(row['Excel_Col']),
                    "original_name": name,
                    "observation": obs,
                    "personal_obs": personal_obs,
                    "classification": clasif
                }
            })
            
    calendar_options = {
        "editable": st.session_state.is_admin,
        "selectable": st.session_state.is_admin,
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",
        "locale": "es",
        "buttonText": {
            "today": "Hoy",
            "month": "Mes"
        },
        "eventDisplay": "block",
        "height": 700
    }
    
    custom_css = \"\"\"
        .fc-event {
            cursor: pointer;
            border-radius: 4px;
            border: 1px solid rgba(0,0,0,0.1);
            padding: 2px 4px;
            font-weight: 500;
            font-family: 'Outfit', sans-serif;
            transition: all 0.2s ease;
        }
        .fc-event:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
    \"\"\"
    
    cal_state = calendar(events=events, options=calendar_options, custom_css=custom_css, key="shifts_calendar")
    
    if st.session_state.is_admin and cal_state.get("eventChange"):
        change = cal_state["eventChange"]
        old_e = change["oldEvent"]
        new_e = change["event"]
        
        old_date_str = old_e["start"].split("T")[0]
        new_date_str = new_e["start"].split("T")[0]
        
        if old_date_str != new_date_str:
            props = old_e["extendedProps"]
            try:
                old_date = datetime.datetime.strptime(old_date_str, "%Y-%m-%d").date()
                new_date = datetime.datetime.strptime(new_date_str, "%Y-%m-%d").date()
                
                if new_date.weekday() != 5:
                    st.error(f"¡Solo se pueden asignar turnos a los sábados! Se intentó mover al {new_date.strftime('%A')}.")
                else:
                    target_sheet = props['sheet']
                    dp.delete_shift_cell(
                        excel_path=st.session_state.excel_path,
                        sheet_name=props['sheet'],
                        row_idx=props['row'],
                        col_idx=props['col'],
                        date_val=old_date,
                        observation="",
                        original_name=props['original_name'],
                        clasificacion="Secuencia Normal"
                    )
                    
                    dp.add_shift_to_date(
                        excel_path=st.session_state.excel_path,
                        sheet_name=target_sheet,
                        target_date=new_date,
                        supernumerary_name=props['original_name'],
                        observation=props['observation'],
                        clasificacion=props['classification']
                    )
                    st.success(f"Turno de {props['original_name']} movido al {new_date_str}.")
                    load_app_data()
                    st.rerun()
            except Exception as e:
                st.error(f"Error al mover turno: {e}")
                
    if st.session_state.is_admin and cal_state.get("eventClick"):
        e = cal_state["eventClick"]["event"]
        props = e["extendedProps"]
        action_details = {
            'date': datetime.datetime.strptime(e["start"].split("T")[0], "%Y-%m-%d").date(),
            'doctor': props['original_name'],
            'row': props['row'],
            'col': props['col'],
            'sheet': props['sheet']
        }
        show_selection_dialog(action_details)
        
    if st.session_state.is_admin and cal_state.get("dateClick"):
        clicked_date_str = cal_state["dateClick"]["date"].split("T")[0]
        clicked_date = datetime.datetime.strptime(clicked_date_str, "%Y-%m-%d").date()
        if clicked_date.weekday() == 5:
            match_on_date = df_shifts[df_shifts['Date'] == clicked_date]
            if not match_on_date.empty:
                sheet_name = match_on_date.iloc[0]['Sheet']
            else:
                xl = pd.ExcelFile(st.session_state.excel_path)
                month_word = dp.MONTH_NAMES_SP.get(clicked_date.month, '').upper()
                flat_sheet_candidate = f"{month_word} {clicked_date.year}"
                if flat_sheet_candidate in xl.sheet_names:
                    sheet_name = flat_sheet_candidate
                else:
                    sheet_name = f"SABADOS {clicked_date.year}"
                    for s in xl.sheet_names:
                        if str(clicked_date.year) in s:
                            sheet_name = s; break
            show_add_dialog(clicked_date, sheet_name)

"""

final_lines = lines[:start_idx + 1] + [new_calendar_code + '\n'] + lines[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print('Calendar inserted successfully.')
