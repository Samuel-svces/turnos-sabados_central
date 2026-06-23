import os

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

search_str = "st.write(f\"**Fecha:** {sat_date.strftime('%A, %d de %B de %Y')}\")"
replacement = """DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    fecha_es = f"{DIAS[sat_date.weekday()]}, {sat_date.day:02d} de {MESES[sat_date.month-1]} de {sat_date.year}"
    st.write(f"**Fecha:** {fecha_es}")"""

if search_str in content:
    content = content.replace(search_str, replacement)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Dates localized successfully!")
else:
    print("Could not find the target string.")
