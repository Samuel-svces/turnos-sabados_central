"""
test_sharepoint_crud.py
-----------------------
Prueba automatizada de integración que valida el ciclo completo de mutaciones
en la Lista de SharePoint 'MODIFICACIONES_SABADOS' a través de data_processor.py:
1. Compilación de módulos Python.
2. AGREGAR un turno nuevo y verificar su persistencia y presencia en load_data().
3. REEMPLAZAR (cambio) del turno y verificar la actualización.
4. ELIMINAR el turno y verificar que deja de ser visible en load_data().
5. Limpieza automática de los registros de prueba en SharePoint.
"""

import os
import sys
import datetime
import py_compile

# Asegurar path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import graph_client as gc
import data_processor as dp

def run_tests():
    print("====================================================================")
    print("  [TEST] Test Suite: Integracion SharePoint CRUD y Carga de Turnos")
    print("====================================================================")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. Compilación limpia
    print("\n[1/5] Verificando compilación de todos los módulos Python...")
    modules = ["app.py", "data_processor.py", "graph_client.py", "ui_dialogs.py", "styles.py"]
    for m in modules:
        m_path = os.path.join(base_dir, m)
        py_compile.compile(m_path, doraise=True)
        print(f"  [OK] {m} compilo sin errores de sintaxis.")

    # 2. Conectividad
    print("\n[2/5] Verificando conexión con Microsoft Graph y SharePoint...")
    assert gc.is_sharepoint_configured(), "SharePoint no está configurado."
    items_initial = gc.get_sharepoint_list_items("modificaciones_sabados")
    print(f"  [OK] Conectado exitosamente. Total registros en SharePoint: {len(items_initial)}")

    # 3. Carga inicial de turnos
    print("\n[3/5] Verificando load_data() maestro + deltas en SharePoint...")
    excel_path = os.path.join(base_dir, "TURNOS SABADOS.xlsx")
    df_shifts, errors = dp.load_data(excel_path)
    assert not df_shifts.empty, "df_shifts no debería estar vacío."
    assert len(errors) == 0, f"Se encontraron errores en carga base: {errors}"
    print(f"  [OK] Carga exitosa: {len(df_shifts)} turnos totales activos. 0 errores.")

    # 4. Ciclo CRUD con Turno de Prueba
    test_date = datetime.date(2026, 12, 26)
    test_doc_add = "MEDICO PRUEBA AGREGAR TEST"
    test_doc_rep = "MEDICO PRUEBA REEMPLAZAR TEST"

    print("\n[4/5] Probando ciclo de vida: AGREGAR -> REEMPLAZAR -> ELIMINAR...")

    # A) AGREGAR
    print(f"  -> A. Insertando AGREGAR para '{test_doc_add}' en {test_date}...")
    dp.save_modification(excel_path, {
        'sheet': 'DICIEMBRE 2026',
        'date': test_date,
        'original_name': '',
        'new_name': test_doc_add,
        'row': 0,
        'col': 0,
        'type': 'AGREGAR',
        'observaciones': 'Test automático AGREGAR',
        'clasificacion': 'Secuencia Normal'
    })

    dp.load_modifications.clear()
    df_after_add, _ = dp.load_data(excel_path)
    mask_add = (df_after_add['Date'] == test_date) & (df_after_add['Supernumerary'] == test_doc_add)
    assert mask_add.any(), f"Error: '{test_doc_add}' no apareció tras AGREGAR."
    print("     [OK] AGREGAR validado: el médico aparece en la programación.")

    # B) REEMPLAZAR
    print(f"  -> B. Insertando REEMPLAZAR: '{test_doc_add}' -> '{test_doc_rep}'...")
    dp.save_modification(excel_path, {
        'sheet': 'DICIEMBRE 2026',
        'date': test_date,
        'original_name': test_doc_add,
        'new_name': test_doc_rep,
        'row': 0,
        'col': 0,
        'type': 'REEMPLAZAR',
        'observaciones': 'Test automático REEMPLAZAR',
        'clasificacion': 'Cambio de turno'
    })

    dp.load_modifications.clear()
    df_after_rep, _ = dp.load_data(excel_path)
    mask_rep = (df_after_rep['Date'] == test_date) & (df_after_rep['Supernumerary'] == test_doc_rep)
    mask_old = (df_after_rep['Date'] == test_date) & (df_after_rep['Supernumerary'] == test_doc_add)
    assert mask_rep.any(), f"Error: '{test_doc_rep}' no apareció tras REEMPLAZAR."
    assert not mask_old.any(), f"Error: '{test_doc_add}' sigue apareciendo tras ser reemplazado."
    print("     [OK] REEMPLAZAR validado: el médico fue sustituido correctamente.")

    # C) ELIMINAR
    print(f"  -> C. Insertando ELIMINAR para '{test_doc_rep}'...")
    dp.save_modification(excel_path, {
        'sheet': 'DICIEMBRE 2026',
        'date': test_date,
        'original_name': test_doc_rep,
        'new_name': '',
        'row': 0,
        'col': 0,
        'type': 'ELIMINAR',
        'observaciones': 'Test automático ELIMINAR',
        'clasificacion': 'Secuencia Normal'
    })

    dp.load_modifications.clear()
    df_after_del, _ = dp.load_data(excel_path)
    mask_rep_del = (df_after_del['Date'] == test_date) & (df_after_del['Supernumerary'] == test_doc_rep)
    assert not mask_rep_del.any(), f"Error: '{test_doc_rep}' sigue apareciendo tras ser eliminado."
    print("     [OK] ELIMINAR validado: el turno desapareció y la eliminación persiste.")

    # 5. Limpieza de registros de prueba
    print("\n[5/5] Limpiando registros de prueba de la Lista de SharePoint...")
    items_now = gc.get_sharepoint_list_items("modificaciones_sabados")
    ids_to_clean = []
    for it in items_now:
        name_t = str(it.get('Title', '')) + str(it.get('ORIGINAL_NAME', '')) + str(it.get('NEW_NAME', ''))
        if "PRUEBA" in name_t:
            ids_to_clean.append(str(it.get('_item_id', it.get('id', ''))))

    if ids_to_clean:
        deleted = gc.delete_sharepoint_list_items_batch("modificaciones_sabados", ids_to_clean)
        print(f"  [OK] {deleted} registros de prueba eliminados de SharePoint.")

    dp.load_modifications.clear()
    print("\n====================================================================")
    print("  [SUCCESS] TODAS LAS PRUEBAS AUTOMATIZADAS PASARON CON EXITO")
    print("====================================================================")
    return True

if __name__ == "__main__":
    run_tests()
