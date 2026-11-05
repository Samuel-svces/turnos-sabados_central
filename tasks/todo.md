# Task Checklist: Purga y Reinicio de Modificaciones en SharePoint

## Fase 1: Creación del Script de Purga y Respaldo CLI
- [x] **Tarea 1.1**: Desarrollar `scripts/purge_all_sharepoint_modificaciones.py` con descarga de respaldo JSON preventivo, soporte `--dry-run` y borrado en lotes `$batch`.

## Fase 2: Incorporación de Botón de Purga Segura en Panel Admin (UI)
- [x] **Tarea 2.1**: En `turnos-sabados_central/app.py`, agregar en la pestaña de administración una sección de mantenimiento con confirmación de seguridad, descarga de respaldo y purga de la lista de SharePoint.
- [x] **Tarea 2.2**: Agregar invalidación de caché local y de sesión tras la purga para reflejar inmediatamente los turnos base del consolidado.

## Fase 3: Verificación y Despliegue
- [x] **Tarea 3.1**: Compilación de código y ejecución de pruebas unitarias (`test_consolidado_historico.py`).
- [ ] **Tarea 3.2**: Subida de commit a GitHub (`origin main`) para desplegar en Streamlit Cloud.
- [ ] **Tarea 3.3**: Ejecución de la purga y validación visual del calendario limpio.
