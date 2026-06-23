import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'dp.save_personal_modification(st.session_state.excel_path, p_data)' in line:
        indent = line[:len(line) - len(line.lstrip())]
        replacement = f"{indent}try:\n{indent}    dp.save_personal_modification(st.session_state.excel_path, p_data)\n{indent}except PermissionError:\n{indent}    st.error(\"⚠️ Error de Permisos: El archivo de Excel está abierto en otra aplicación. Por favor, ciérralo y vuelve a intentarlo.\")\n{indent}    st.stop()\n"
        lines[i] = replacement

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Replaced PermissionError handlers successfully!')
