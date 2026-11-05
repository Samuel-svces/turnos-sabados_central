# Task Checklist: Nueva Conexión SharePoint y Consolidado Histórico

## Fase 1: Limpieza de Secretos y Configuración de Conexión
- [x] **Tarea 1.1**: Limpiar `turnos-sabados_central/.streamlit/secrets.toml` retirando variables de archivos Excel antiguos y agregando `consolidado_conexion = "7B4DC31EBF-4E2F-4399-BC10-D2B224AAA12B%7D"` conservando `admin_password`.
- [x] **Tarea 1.2**: Actualizar `graph_client.py` para parsear y normalizar el GUID de `consolidado_conexion` y generar las URLs de descarga de SharePoint.

## Fase 2: Implementación de la Lógica de Validación de Turnos
- [x] **Tarea 2.1**: Implementar en `data_processor.py` la lectura de las hojas `CONSOLIDADO 2026 HISTORICO` y `SUPERNUMERARIO 2026 HISTORICO`.
- [x] **Tarea 2.2**: Implementar el filtro en `CONSOLIDADO 2026 HISTORICO`: `FECHA CUBRIMIENTO` es sábado y fecha >= 31 de octubre de 2026.
- [x] **Tarea 2.3**: Implementar la validación cruzada y alternancia de sábados con `SUPERNUMERARIO 2026 HISTORICO`:
  - Secuencia 31 Octubre (pares): coincidencia de `NOMBRE SUPER VALIDADO` con `Nombre` y `Restriccion` == `"sin restriccion"`.
  - Sábado contrario (impares): coincidencia de `NOMBRE SUPER VALIDADO` con `Nombre` y `Restriccion` == `"con restriccion"`.
- [x] **Tarea 2.4**: Actualizar `load_supernumeraries()` y `get_allowed_doctors(target_date)` para alimentar el directorio de profesionales y filtrar dinámicamente los menús desplegables según la alternancia del sábado seleccionado.

## Fase 3: Integración y Blindaje de Procesos Existentes
- [x] **Tarea 3.1**: Asegurar que `load_data()` integre los turnos validados con la Lista de SharePoint de modificaciones (`MODIFICACIONES_SABADOS`) sin afectar los procesos de reemplazo/eliminación/adición.
- [x] **Tarea 3.2**: Manejar resiliencia de nombres de hojas (`2026` vs `20206`) y nombres de columnas (tildes, mayúsculas, espacios).

## Fase 4: Pruebas y Verificación
- [x] **Tarea 4.1**: Crear suite de pruebas `tests/test_consolidado_historico.py` con datos simulados y validación de reglas de negocio (6/6 aprobados).
- [x] **Tarea 4.2**: Compilación limpia de todos los módulos Python (`py_compile`).
- [x] **Tarea 4.3**: Verificación integral de interoperabilidad entre módulos.
