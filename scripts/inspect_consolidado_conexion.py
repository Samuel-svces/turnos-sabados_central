"""
inspect_consolidado_conexion.py
Descarga y analiza las hojas del archivo maestro 'CONSOLIDADO CONEXION' desde SharePoint.
"""
import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import graph_client as gc

def inspect():
    print("Conectando a SharePoint...")
    if not gc.is_sharepoint_configured():
        print("SharePoint no configurado.")
        return

    buf = gc.download_excel("consolidado_conexion")
    cache_path = os.path.join(BASE_DIR, ".cache", "CONSOLIDADO_CONEXION_cached.xlsx")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "wb") as f:
        f.write(buf.getvalue())
    print(f"Archivo guardado en {cache_path}")

    xl = pd.ExcelFile(cache_path)
    print("\nHojas disponibles:", xl.sheet_names)

    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        print(f"\n--- Hoja: '{sheet}' ({len(df)} filas, {len(df.columns)} columnas) ---")
        print("Columnas:", df.columns.tolist())
        print("Primeras 3 filas:")
        print(df.head(3))
        
        # Analizar fechas si tiene columna fecha
        for c in df.columns:
            if "fecha" in str(c).lower():
                print(f"Valores únicos en columna de fecha '{c}':")
                print(df[c].value_counts(dropna=False).head(20))
            if "restric" in str(c).lower():
                print(f"Valores únicos en columna de restricción '{c}':")
                print(df[c].value_counts(dropna=False))

if __name__ == "__main__":
    inspect()
