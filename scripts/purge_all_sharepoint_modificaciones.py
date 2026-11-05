"""
purge_all_sharepoint_modificaciones.py
---------------------------------------
1. Descarga y respalda de manera preventiva todos los registros actuales de la Lista de SharePoint
   'MODIFICACIONES_SABADOS' en un archivo JSON fechado dentro de la carpeta 'backups/'.
2. Pone a disposición la purga completa de los registros residuales acumulados (AGREGAR, REEMPLAZAR, ELIMINAR)
   usando peticiones optimizadas en lotes ($batch de Microsoft Graph en paquetes de 20).
3. Verifica el estado y conteo final de la lista para garantizar que quede limpia.
4. Admite las opciones:
     --dry-run : Muestra el análisis y guarda el respaldo sin eliminar ningún elemento.
     --force   : Ejecuta la purga directa sin solicitar confirmación manual por teclado.
"""

import os
import sys
import json
import datetime
import argparse
import pandas as pd

# Asegurar path para importar módulos locales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import graph_client as gc


def run_purge(dry_run: bool = False, force: bool = False) -> bool:
    print("=" * 72)
    print("  [PURGE] Depuración Total de Registros en Lista SharePoint 'MODIFICACIONES_SABADOS'")
    print("=" * 72)

    if not gc.is_sharepoint_configured():
        print("[ERROR] Credenciales de Azure AD / SharePoint no configuradas.")
        print("Asegúrese de contar con tenant_id, client_id, client_secret y list_id_mod_sab.")
        return False

    print("\n[1/4] Consultando elementos de la lista en SharePoint...")
    items = gc.get_sharepoint_list_items("modificaciones_sabados")
    total_items = len(items)
    print(f"-> Total de elementos recuperados: {total_items}")

    # 1. Crear respaldo preventivo
    backup_dir = os.path.join(BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"sharepoint_modificaciones_backup_{timestamp_str}.json")

    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[2/4] [OK] Respaldo de seguridad guardado en: {backup_file}")

    if total_items == 0:
        print("\n[INFO] La lista de SharePoint ya se encuentra vacía. No hay elementos para purgar.")
        return True

    # 2. Desglose analítico
    df = pd.DataFrame(items)
    print("\nDesglose de elementos por TYPE:")
    if "TYPE" in df.columns:
        print(df["TYPE"].value_counts().to_string())
    else:
        print("  (Columna TYPE no presente en los registros)")

    # 3. Recopilar IDs para purga
    item_ids = []
    for it in items:
        raw_id = it.get("_item_id", it.get("id"))
        if raw_id:
            item_ids.append(str(raw_id))

    print(f"\nTotal IDs listos para eliminación: {len(item_ids)}")

    if dry_run:
        print("\n[DRY RUN] Simulación finalizada. No se borró ningún elemento en SharePoint.")
        print(f"El respaldo preventivo quedó disponible en: {backup_file}")
        return True

    if not force:
        confirm = input("\n¿Está seguro de eliminar TODOS los registros de modificaciones en SharePoint? (s/N): ").strip().lower()
        if confirm not in ("s", "si", "y", "yes"):
            print("[CANCELADO] Operación cancelada por el usuario.")
            return False

    # 4. Ejecución en lotes de 20
    print(f"\n[3/4] Purgando {len(item_ids)} elementos en lotes de 20 vía Microsoft Graph API...")
    deleted_count = gc.delete_sharepoint_list_items_batch("modificaciones_sabados", item_ids)
    print(f"-> Elementos eliminados exitosamente: {deleted_count} de {len(item_ids)}")

    # 5. Verificación de lista vacía
    print("\n[4/4] Verificando estado final de la lista en SharePoint...")
    items_after = gc.get_sharepoint_list_items("modificaciones_sabados")
    print(f"-> Conteo de elementos restantes: {len(items_after)}")

    if len(items_after) == 0:
        print("\n[EXITO] La lista de modificaciones de SharePoint ha sido vaciada por completo.")
    else:
        print(f"\n[ADVERTENCIA] Quedaron {len(items_after)} elementos sin eliminar. Puede volver a ejecutar el script.")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Purgar lista de modificaciones de SharePoint con respaldo previo")
    parser.add_argument("--dry-run", action="store_true", help="Solo generar respaldo y análisis sin eliminar")
    parser.add_argument("--force", action="store_true", help="Omitir solicitud de confirmación interactiva")
    args = parser.parse_args()

    run_purge(dry_run=args.dry_run, force=args.force)
