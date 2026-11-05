# AGENTS.md

## Regla principal: consultar las skills antes de cada requerimiento

Antes de analizar, planear o implementar cualquier requerimiento:

1. Revisar las skills disponibles en `.agents/skills/` (empezando por `using-agent-skills/SKILL.md`).
2. Identificar la fase del trabajo y cargar con la herramienta `skill` las skills aplicables.
3. Seguir el flujo de la skill elegida, incluidos sus pasos de verificación.
4. Si el trabajo toca UI, cargar además `frontend-ui-engineering`.

No implementar nada sin haber consultado antes las skills que apliquen.

## Contexto del proyecto

- Aplicación Streamlit: `app.py` (interfaz), `styles.py` (CSS inyectado), `ui_dialogs.py` (diálogos), `data_processor.py` (datos), `graph_client.py` (SharePoint/Graph).
- Los estilos visuales viven en `styles.py` dentro de `apply_styles()`.
- Responder en español.
- Cambios de UI: mínimos y quirúrgicos, respetando el sistema de estilos existente (paleta, radios, espaciados, sombras).

## Imágenes de referencia

Si el modelo activo no puede interpretar imágenes, no asumir lo que muestra la captura: confirmar con el usuario el elemento exacto antes de modificar el diseño.
