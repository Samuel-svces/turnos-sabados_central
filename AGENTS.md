# AGENTS.md

## Regla Absoluta y Mandatoria: Consultar Estrictamente `gstack-main` y las Skills antes de cada requerimiento

Antes de analizar, planear, responder o implementar CUALQUIER requerimiento:

1. **Paso Obligatorio por `gstack-main`**:
   - Consultar la carpeta `gstack-main/` (especialmente `gstack-main/SKILL.md`, `gstack-main/AGENTS.md` y `gstack-main/ETHOS.md`).
   - Aplicar los 8 Principios del Ethos de gstack:
     1. **Boil the Ocean**: Cobertura total de los requerimientos y casos de borde con el código mínimo necesario.
     2. **Search Before Building**: Verificar el código, patrones y utilidades existentes antes de reinventar.
     3. **User Sovereignty**: El usuario decide siempre. La IA recomienda, consulta y no toma atajos.
     4. **Honest Work**: El trabajo real se valida con pruebas reales automatizadas. Cero auto-certificación sin evidencia.
     5. **Attack the Premise**: Cuando algo falle, cuestionar y comprobar la premisa subyacente.
     6. **Separate Before Serializing**: Evitar colisiones en el estado compartido mediante separación de responsabilidades.
     7. **Make Operations Idempotent**: Diseñar para que cualquier operación pueda re-ejecutarse con seguridad.
     8. **Explain the Number / Evidence**: Demostrar los cambios con pruebas verificadas y evidencia medible.

2. **Enrutamiento por Skills de `gstack-main` y `.agents/skills/`**:
   - Nuevas ideas o aclaración de requisitos: `/office-hours`, `/spec`, `interview-me`.
   - Diagnóstico o corrección de bugs: `/investigate`, `debugging-and-error-recovery`.
   - Diseño, interfaz y componentes visuales: `frontend-ui-engineering`, `/design-review`, `/design-html`.
   - Pruebas y validación funcional: `/qa`, `/qa-only`, `test-driven-development`.
   - Revisión de arquitectura, calidad y diffs: `/review`, `code-review-expert`, `code-simplification`.
   - Despliegues y commits atómicos: `/ship`, `git-workflow-and-versioning`.

3. **No implementar nada sin haber consultado y aplicado el flujo de las skills correspondientes.**

## Contexto del Proyecto

- Aplicación Streamlit: `app.py` (interfaz principal), `componentes/` (cuadrícula, buscador, cabecera, diálogos), `estilos/styles.py` (CSS centralizado), `modulos/` (procesador de datos, cliente SharePoint), `tests/` (suites de pruebas automatizadas).
- Idioma obligatorio: Todo mensaje, diálogo y comunicación con el usuario debe ser en español.
- Cambios de UI: Mínimos, quirúrgicos, y respetando la paleta institucional (`#F0FBFB`, `#0f9a9b`, `#17243D`, `#ccebee`).
- Verificación continua: Todas las pruebas unitarias (`python -m unittest discover -s tests`) deben ejecutarse y mantenerse en verde (19/19) antes de dar por completado cualquier requerimiento.

## Imágenes de Referencia

Si el modelo activo no puede interpretar imágenes, no asumir lo que muestra la captura: confirmar con el usuario el elemento exacto antes de modificar el diseño.
