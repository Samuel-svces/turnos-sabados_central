# Task Checklist: Conexión Directa SharePoint Graph, Filtro Estricto y Optimización

## Fase 1: Conexión Directa a SharePoint Graph y Filtro Estricto de Supernumerarios
- [x] **Tarea 1.1**: En `data_processor.py`, implementar filtro estricto en `load_supernumeraries`:
  - `Fecha >= 2026-10-01` obligatorio (descartar fechas anteriores o nulas).
  - `Cedula` obligatoria (descartar vacíos, nulos, `"nan"`, `"0"`).
  - Limpieza de notas y nombres.
  - Priorizar conexión directa vía `_use_sharepoint()` y Graph API sin depender de archivos locales desactualizados.
- [x] **Tarea 1.2**: En `ui_dialogs.py`, asegurar que `get_allowed_doctors` retorne exclusivamente los supernumerarios que cumplan las condiciones anteriores.

## Fase 2: Remoción de la Pestaña "Directorio y Sincronización"
- [x] **Tarea 2.1**: En `app.py`, eliminar `st.tabs` y el bloque `tab_admin`. Cargar directamente la vista de calendario en contenedor principal.
- [x] **Tarea 2.2**: Reubicar la sección de purga y mantenimiento dentro del menú de administración ⚙️.

## Fase 3: Optimización de Rendimiento en Carga y Eliminación
- [x] **Tarea 3.1**: Optimizar `delete_shift_callback` y `save_changes_callback` con actualización directa e inmediata en memoria (`st.session_state.shifts_df`) y sincronización por lotes.
- [x] **Tarea 3.2**: Optimizar la carga en `app.py` para reutilizar `super_df` en memoria sin re-parsear repetitivamente.

## Fase 4: Verificación Integral y Despliegue
- [x] **Tarea 4.1**: Ejecutar suite automatizada de pruebas `tests/test_consolidado_historico.py`.
- [x] **Tarea 4.2**: Probar carga directa y verificar que los nombres de julio/agosto o sin cédula no aparezcan.
- [x] **Tarea 4.3**: Commit y preparar comando de despliegue a GitHub.
