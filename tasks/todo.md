# Task Checklist: Resolución de Error de Conexión en Streamlit Cloud

## Fase 1: Diagnóstico y Robustecimiento de Endpoints en Graph API
- [ ] **Tarea 1.1**: En `graph_client.py`, agregar las rutas directas de SharePoint por `drive_id` por defecto con `{guid}`, `SHAREPOINT_SITE_ID`, y corregir la sintaxis de ruta de sitio (`site_base:/drive/...`).
- [ ] **Tarea 1.2**: Mejorar el reporte de errores en `graph_client.py` para devolver los códigos HTTP y respuestas detalladas de Microsoft Graph.

## Fase 2: Desacoplamiento de Metadatos y Manejo de Errores en data_processor
- [ ] **Tarea 2.1**: En `data_processor.py`, permitir que `_open_consolidado_conexion()` intente `download_excel` directamente si la consulta de metadatos falla.
- [ ] **Tarea 2.2**: Si la descarga de SharePoint falla en la nube, propagar el error técnico exacto en vez de enmascararlo con "No se pudo cargar el archivo".

## Fase 3: Asistente Visual de Diagnóstico en la UI (app.py)
- [ ] **Tarea 3.1**: En `app.py`, detectar si faltan variables en `st.secrets` (`tenant_id`, `client_id`, `client_secret`, `consolidado_conexion`) y mostrar una guía paso a paso en pantalla para configurarlos en el panel de Streamlit Cloud.
- [ ] **Tarea 3.2**: Mostrar el detalle técnico completo del error de SharePoint si ocurre un fallo de autenticación o búsqueda.

## Fase 4: Verificación
- [ ] **Tarea 4.1**: Ejecutar suite de pruebas unitarias (`test_consolidado_historico.py`).
- [ ] **Tarea 4.2**: Compilación limpia de todos los módulos Python (`py_compile`).
