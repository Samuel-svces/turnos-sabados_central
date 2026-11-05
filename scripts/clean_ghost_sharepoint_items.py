"""
clean_ghost_sharepoint_items.py
--------------------------------
1. Descarga y respalda en un archivo JSON local todos los elementos actuales de la lista
   de SharePoint 'MODIFICACIONES_SABADOS'.
2. Identifica los 450 registros huérfanos de tipo 'ELIMINAR' generados el 22 de octubre
   de 2026 por el antiguo botón de 'Duplicar'.
3. Elimina dichos registros usando peticiones en lote ($batch de Microsoft Graph).
4. Verifica el estado final y el conteo limpio de la lista.
"""

import os
import sys
import json
import datetime
import pandas as pd

# Asegurar path para importar graph_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import graph_client as gc

def backup_and_clean_ghost_items(dry_run: bool = False):
    print("====================================================================")
    print("  [CLEAN] Purga y Respaldo de Registros Residuales en SharePoint List")
    print("====================================================================")
    
    if not gc.is_sharepoint_configured():
        print("[ERROR] Credenciales de Azure AD no configuradas.")
        return False

    print("\n[1/4] Descargando todos los elementos de la Lista de SharePoint...")
    items = gc.get_sharepoint_list_items("modificaciones_sabados")
    total_items = len(items)
    print(f"-> Total elementos recuperados: {total_items}")

    # 1. Crear carpeta de respaldos y guardar JSON
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backup_dir = os.path.join(base_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"sharepoint_modificaciones_backup_{timestamp}.json")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n[2/4] [OK] Respaldo completo guardado en: {backup_file}")

    # 2. Analizar registros
    df = pd.DataFrame(items)
    print("\nDesglose actual de elementos por TYPE:")
    if "TYPE" in df.columns:
        print(df["TYPE"].value_counts().to_string())
    else:
        print("No se encontró columna TYPE.")

    # 3. Filtrar registros huérfanos de ELIMINAR creados el 22/10/2026
    # Estos 450 registros fueron generados por la versión previa del botón 'Duplicar'
    ghost_ids = []
    for it in items:
        m_type = str(it.get("TYPE", "")).strip().upper()
        created_str = str(it.get("Created", ""))
        item_id = str(it.get("_item_id", it.get("id", "")))
        
        if m_type == "ELIMINAR" and "2026-10-22" in created_str and item_id:
            ghost_ids.append(item_id)

    print(f"\n[3/4] Registros residuales 'ELIMINAR' identificados para purga: {len(ghost_ids)}")

    if dry_run:
        print("[DRY RUN] No se eliminaron elementos de SharePoint. Ejecute con dry_run=False para aplicar.")
        return True

    if not ghost_ids:
        print("[INFO] No se encontraron registros huérfanos para purgar.")
        return True

    # 4. Eliminar en lotes usando Graph $batch
    print(f"Purgando {len(ghost_ids)} elementos en lotes de 20 vía Microsoft Graph API...")
    deleted_count = gc.delete_sharepoint_list_items_batch("modificaciones_sabados", ghost_ids)
    print(f"-> Elementos eliminados exitosamente: {deleted_count} de {len(ghost_ids)}")

    # 5. Validación final
    print("\n[4/4] Verificando estado final de la Lista de SharePoint...")
    items_after = gc.get_sharepoint_list_items("modificaciones_sabados")
    df_after = pd.DataFrame(items_after)
    print(f"-> Total elementos tras la purga: {len(items_after)}")
    print("Desglose final de elementos por TYPE:")
    if "TYPE" in df_after.columns:
        print(df_after["TYPE"].value_counts().to_string())

    print("\n====================================================================")
    print("  [EXITO] Purga y validación completadas con éxito.")
    print("====================================================================")
    return True

if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    backup_and_clean_ghost_items(dry_run=is_dry)
