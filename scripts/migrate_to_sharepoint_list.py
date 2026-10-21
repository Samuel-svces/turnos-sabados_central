import os
import datetime
import pandas as pd
import requests
import msal
import time
import math

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import graph_client as gc

SITE_ID = gc.SHAREPOINT_SITE_ID
LIST_ID = gc._get_list_id('modificaciones_sabados')

def get_token():
    return gc._get_access_token()

def migrate_modifications(dry_run=False, limit=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "MODIFICACIONES_SABADOS.xlsx")
    
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} no encontrado")
        return
        
    df = pd.read_excel(excel_path, sheet_name="MODIFICACIONES")
    # Filtrar estrictamente solo AGREGAR y REEMPLAZAR
    df = df[df['TYPE'].isin(['AGREGAR', 'REEMPLAZAR'])].copy()
    
    if limit:
        df = df.head(limit)
        
    total_records = len(df)
    print(f"Total registros a migrar: {total_records}")
    
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Preparar payload items
    items_to_insert = []
    for idx, row in df.iterrows():
        # Formatear fecha
        d_val = row.get('DATE')
        d_iso = None
        if pd.notna(d_val):
            try:
                dt = pd.to_datetime(d_val)
                d_iso = dt.strftime("%Y-%m-%dT00:00:00Z")
            except Exception:
                pass
                
        doc_title = str(row.get('NEW_NAME') if pd.notna(row.get('NEW_NAME')) and row.get('NEW_NAME') else row.get('ORIGINAL_NAME', '')).strip().upper()
        if not doc_title:
            doc_title = "TURNO MODIFICADO"
            
        fields = {
            'Title': doc_title,
            'ORIGINAL_NAME': str(row.get('ORIGINAL_NAME', '')).strip().upper() if pd.notna(row.get('ORIGINAL_NAME')) else '',
            'NEW_NAME': str(row.get('NEW_NAME', '')).strip().upper() if pd.notna(row.get('NEW_NAME')) else '',
            'TYPE': str(row.get('TYPE', '')).strip().upper(),
            'SHEET': str(row.get('SHEET', 'SABADOS 2026')).strip(),
            'CLASIFICACION': str(row.get('CLASIFICACION', 'Secuencia Normal')).strip() if pd.notna(row.get('CLASIFICACION')) else 'Secuencia Normal',
            'OBSERVACIONES': str(row.get('OBSERVACIONES', '')).strip() if pd.notna(row.get('OBSERVACIONES')) else '',
            'ROW': int(row.get('ROW', 0)) if pd.notna(row.get('ROW')) else 0,
            'COL': int(row.get('COL', 0)) if pd.notna(row.get('COL')) else 0,
        }
        if d_iso:
            fields['FECHA'] = d_iso
            
        items_to_insert.append(fields)
        
    print(f"Preparados {len(items_to_insert)} elementos.")
    
    if dry_run:
        print("[DRY RUN] Ejemplo de elemento 1:", items_to_insert[0])
        return
        
    # Enviar en lotes usando Graph $batch (hasta 20 por petición)
    batch_size = 20
    num_batches = math.ceil(len(items_to_insert) / batch_size)
    
    inserted_count = 0
    errors_count = 0
    
    start_time = time.time()
    
    for b_idx in range(num_batches):
        batch_slice = items_to_insert[b_idx * batch_size : (b_idx + 1) * batch_size]
        
        requests_payload = []
        for i_idx, item in enumerate(batch_slice):
            requests_payload.append({
                'id': str(i_idx + 1),
                'method': 'POST',
                'url': f'/sites/{SITE_ID}/lists/{LIST_ID}/items',
                'headers': {'Content-Type': 'application/json'},
                'body': {'fields': item}
            })
            
        batch_body = {'requests': requests_payload}
        
        try:
            r = requests.post('https://graph.microsoft.com/v1.0/$batch', headers=headers, json=batch_body, timeout=30)
            if r.status_code == 200:
                resp_data = r.json()
                for resp in resp_data.get('responses', []):
                    if resp.get('status') in (200, 201):
                        inserted_count += 1
                    else:
                        errors_count += 1
                        print(f"Error en item batch: {resp.get('body')}")
            else:
                print(f"Batch {b_idx + 1} HTTP error {r.status_code}: {r.text[:200]}")
                errors_count += len(batch_slice)
        except Exception as e:
            print(f"Excepción en batch {b_idx + 1}: {e}")
            errors_count += len(batch_slice)
            
        if (b_idx + 1) % 5 == 0 or b_idx == num_batches - 1:
            elapsed = time.time() - start_time
            print(f"Progreso: {inserted_count}/{total_records} insertados ({b_idx + 1}/{num_batches} lotes) en {elapsed:.1f}s")
            
    print(f"\n[FIN MIGRACIÓN] Insertados exitosamente: {inserted_count} | Errores: {errors_count}")

if __name__ == "__main__":
    import sys
    limit_val = int(sys.argv[1]) if len(sys.argv) > 1 else None
    migrate_modifications(limit=limit_val)
