"""
test_consolidado_historico.py
-----------------------------
Prueba unitaria automatizada para validar:
1. Normalización y limpieza del GUID de SharePoint.
2. Lectura y validación de turnos desde las hojas CONSOLIDADO 2026 HISTORICO y SUPERNUMERARIO 2026 HISTORICO.
3. Regla de alternancia de sábados a partir del 31 de octubre de 2026:
   - Secuencia A (31 Oct, 14 Nov, etc.): médicos con 'sin restriccion'.
   - Secuencia B (Sábado contrario: 7 Nov, 21 Nov, etc.): médicos con 'con restriccion'.
4. Filtro estricto: solo sábados y fechas >= 31 de octubre de 2026.
5. Filtrado dinámico por fecha en menús desplegables (get_allowed_doctors).
"""

import os
import sys
import datetime
import tempfile
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import graph_client as gc
import data_processor as dp
import ui_dialogs as ud

def run_tests():
    print("====================================================================")
    print("  [TEST] Suite: Validación Consolidado Histórico y Turnos de Sábados")
    print("====================================================================")

    # 1. Test GUID Cleaner
    print("\n[1/5] Verificando limpieza y normalización del GUID de SharePoint...")
    raw_guid = "7B4DC31EBF-4E2F-4399-BC10-D2B224AAA12B%7D"
    clean_guid = gc._clean_guid(raw_guid)
    expected_guid = "4DC31EBF-4E2F-4399-BC10-D2B224AAA12B"
    assert clean_guid == expected_guid, f"Error en _clean_guid: esperado '{expected_guid}', obtenido '{clean_guid}'"
    print(f"  [OK] GUID procesado correctamente: {clean_guid}")

    # 2. Test URL Builder
    print("\n[2/5] Verificando generación de URLs para Microsoft Graph...")
    urls = gc._file_urls("consolidado_conexion")
    assert len(urls) > 0, "No se generaron URLs para consolidado_conexion"
    assert any(clean_guid in u for u in urls), f"El GUID no aparece en las URLs generadas: {urls}"
    print(f"  [OK] Se generaron {len(urls)} rutas candidatas para Graph API.")

    # 3. Crear Excel de prueba en memoria / temporal
    print("\n[3/5] Creando Excel de prueba con datos simulados...")
    fd, temp_excel_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)

    df_super_test = pd.DataFrame([
        {"Nombre": "CARLOS PEREZ", "Restriccion": "sin restriccion", "Cedula": "1001", "Cargo": "Supernumerario"},
        {"Nombre": "MARIA GOMEZ", "Restriccion": "sin restriccion", "Cedula": "1002", "Cargo": "Supernumerario"},
        {"Nombre": "JUAN RODRIGUEZ", "Restriccion": "con restriccion", "Cedula": "1003", "Cargo": "Supernumerario"},
        {"Nombre": "ANA MARTINEZ", "Restriccion": "con restriccion", "Cedula": "1004", "Cargo": "Supernumerario"}
    ])

    df_consol_test = pd.DataFrame([
        # Caso 1: Sábado 31 Oct (Secuencia A) + Sin Restricción -> DEBE PASAR en 31 Oct
        {"FECHA CUBRIMIENTO": "2026-10-31", "NOMBRE SUPER VALIDADO": "CARLOS PEREZ", "OBSERVACION": "Normal 31 Oct"},
        # Caso 2: Sábado 31 Oct + Con Restricción -> DEBE PASAR AL SÁBADO CONTRARIO (7 Nov)
        {"FECHA CUBRIMIENTO": "2026-10-31", "NOMBRE SUPER VALIDADO": "ANA MARTINEZ", "OBSERVACION": "31 Oct con restriccion -> sábado contrario 7 Nov"},
        # Caso 3: Fecha anterior al 31 de Octubre (24 Oct) -> DEBE SER DESCARTADO
        {"FECHA CUBRIMIENTO": "2026-10-24", "NOMBRE SUPER VALIDADO": "CARLOS PEREZ", "OBSERVACION": "Antes del 31 oct"},
        # Caso 4: Día entre semana (4 Nov - Miércoles) -> DEBE SER DESCARTADO
        {"FECHA CUBRIMIENTO": "2026-11-04", "NOMBRE SUPER VALIDADO": "CARLOS PEREZ", "OBSERVACION": "Miercoles no es sabado"},
        # Caso 5: Médico no registrado en hoja de supernumerarios -> DEBE SER DESCARTADO
        {"FECHA CUBRIMIENTO": "2026-10-31", "NOMBRE SUPER VALIDADO": "MEDICO FANTASMA", "OBSERVACION": "No existe"},
        # Caso 6: Sábado 14 Nov (Secuencia A) + Sin Restricción -> DEBE PASAR en 14 Nov
        {"FECHA CUBRIMIENTO": "2026-11-14", "NOMBRE SUPER VALIDADO": "MARIA GOMEZ", "OBSERVACION": "Normal 14 Nov"}
    ])

    with pd.ExcelWriter(temp_excel_path, engine="openpyxl") as writer:
        df_consol_test.to_excel(writer, sheet_name="CONSOLIDADO 2026 HISTORICO", index=False)
        df_super_test.to_excel(writer, sheet_name="SUPERNUMERARIO 2026 HISTORICO", index=False)

    try:
        # 4. Probar _get_base_shifts_df contra el archivo de prueba
        print("\n[4/5] Probando _get_base_shifts_df() y reglas de alternancia...")
        dp._get_base_shifts_df.clear()
        df_shifts, errors = dp._get_base_shifts_df(temp_excel_path)
        print(f"  -> Total turnos validados obtenidos: {len(df_shifts)}")
        print(df_shifts[["Date", "Supernumerary", "Observation"]])

        # Validar que los casos 1, 2 y 6 pasaron (total 3 turnos)
        assert len(df_shifts) == 3, f"Esperados 3 turnos válidos, se obtuvieron {len(df_shifts)}"

        # Verificar 31 Oct
        s_31 = df_shifts[df_shifts["Date"] == datetime.date(2026, 10, 31)]
        assert len(s_31) == 1, "Debería haber 1 turno el 31 Oct"
        assert s_31.iloc[0]["Supernumerary"] == "CARLOS PEREZ", "31 Oct debe ser CARLOS PEREZ"

        # Verificar 07 Nov (derivado de los que en 31 Oct tenían Con Restricción)
        s_07 = df_shifts[df_shifts["Date"] == datetime.date(2026, 11, 7)]
        assert len(s_07) == 1, "Debería haber 1 turno el 7 Nov (sábado contrario de 31 Oct)"
        assert s_07.iloc[0]["Supernumerary"] == "ANA MARTINEZ", "7 Nov debe ser ANA MARTINEZ"

        # Verificar 14 Nov
        s_14 = df_shifts[df_shifts["Date"] == datetime.date(2026, 11, 14)]
        assert len(s_14) == 1, "Debería haber 1 turno el 14 Nov"
        assert s_14.iloc[0]["Supernumerary"] == "MARIA GOMEZ", "14 Nov debe ser MARIA GOMEZ"

        print("  [OK] Validaciones de turnos correctas según reglas de alternancia y fechas.")

        # 5. Probar carga de supernumerarios y filtrado dinámico en desplegables
        print("\n[5/5] Probando carga de supernumerarios y filtrado dinámico por fecha...")
        dp.load_supernumeraries.clear()
        df_super_loaded = dp.load_supernumeraries(temp_excel_path)
        assert len(df_super_loaded) == 4, f"Se esperaban 4 supernumerarios, se obtuvieron {len(df_super_loaded)}"
        assert "RESTRICCION" in df_super_loaded.columns, "Falta columna RESTRICCION en df_super"

        # Simular sesión streamlit para ud.get_allowed_doctors
        import streamlit as st
        st.session_state["super_df"] = df_super_loaded
        st.session_state["shifts_df"] = df_shifts

        # Para sábado 31 Oct (Secuencia A) -> Debe mostrar solo CARLOS PEREZ y MARIA GOMEZ
        allowed_31 = ud.get_allowed_doctors(target_date=datetime.date(2026, 10, 31))
        print(f"  -> Médicos permitidos para 31 Oct (Sin Restricción): {allowed_31}")
        assert set(allowed_31) == {"CARLOS PEREZ", "MARIA GOMEZ"}, f"Filtro 31 Oct incorrecto: {allowed_31}"

        # Para sábado 7 Nov (Secuencia B / Contrario) -> Debe mostrar solo JUAN RODRIGUEZ y ANA MARTINEZ
        allowed_07 = ud.get_allowed_doctors(target_date=datetime.date(2026, 11, 7))
        print(f"  -> Médicos permitidos para 7 Nov (Con Restricción): {allowed_07}")
        assert set(allowed_07) == {"JUAN RODRIGUEZ", "ANA MARTINEZ"}, f"Filtro 7 Nov incorrecto: {allowed_07}"

        print("  [OK] Filtrado dinámico en menús desplegables validado con éxito.")

        # 6. Probar load_data() integral con las modificaciones
        print("\n[6/6] Probando load_data() con sobreescritura delta...")
        df_final_data, data_errors = dp.load_data(temp_excel_path)
        assert not df_final_data.empty, "load_data() no debe retornar DataFrame vacío"
        assert len(data_errors) == 0, f"load_data() tuvo errores inesperados: {data_errors}"
        assert len(df_final_data) >= 3, f"load_data() debe contener al menos los 3 turnos base, tiene {len(df_final_data)}"
        print(f"  [OK] load_data() ejecutado correctamente: {len(df_final_data)} turnos activos.")

    finally:
        if os.path.exists(temp_excel_path):
            try:
                os.remove(temp_excel_path)
            except Exception:
                pass

    print("\n====================================================================")
    print("  [SUCCESS] ¡Todas las pruebas unitarias pasaron exitosamente (6/6)!")
    print("====================================================================")

if __name__ == "__main__":
    run_tests()
