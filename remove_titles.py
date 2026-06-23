import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if 'tabs_list = ["Calendario de Turnos"]' in line:
        start_idx = i
        break

end_idx = -1
for i, line in enumerate(lines):
    if 'Programación Mensual de Sábados' in line and '<i class=' in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_code = """# Navigation Tabs
if st.session_state.is_admin:
    tabs = st.tabs(["Calendario de Turnos", "Directorio y Sincronización"])
    tab_calendar = tabs[0]
    tab_admin = tabs[1]
else:
    tab_calendar = st.container()

from streamlit_sortables import sort_items

with tab_calendar:
"""
    final_lines = lines[:start_idx] + [new_code] + lines[end_idx+1:]
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    print('Titles removed successfully!')
else:
    print('Could not find the target lines.')
