# Task Checklist: Reestructuración de Turnos en Excel Online

## Fase 1: Respaldo y Depuración de Datos
- [x] **Tarea 1.1**: Crear script de respaldo y depuración de `MODIFICACIONES_SABADOS.xlsx` (`clean_modifications.py`).
- [x] **Tarea 1.2**: Ejecutar la depuración para remover los 516 registros de `ELIMINAR` accidentales, conservando todos los `AGREGAR` y `REEMPLAZAR`.
- [x] **Tarea 1.3**: Validar la integridad del nuevo archivo Excel y la restauración de los turnos en `load_data()`.

## Checkpoint 1: Integridad de Datos Restaurada
- [x] 0 registros de tipo `ELIMINAR` en el libro delta.
- [x] Todos los médicos de sábados futuros vuelven a ser visibles en el DataFrame de turnos (1.247 turnos totales restaurados).

---

## Fase 2: Corrección de Errores de Código y SharePoint
- [x] **Tarea 2.1**: Conectar la nueva Lista de SharePoint `MODIFICACIONES_SABADOS` vía Graph API y migrar los 1.129 registros limpios.
- [x] **Tarea 2.2**: Corregir en `graph_client.py` las funciones duplicadas (`is_sharepoint_configured`), llamadas residuales y agregar métodos de lista (`get_sharepoint_list_items`, `add_sharepoint_list_item`, `add_sharepoint_list_items_batch`, `delete_sharepoint_list_item`).
- [x] **Tarea 2.3**: En `data_processor.py`, implementar persistencia y lectura directa de la Lista de SharePoint con respaldo local.
- [x] **Tarea 2.4**: Blindar `load_data` para proteger los turnos base contra cualquier intento de eliminación y corregir el seguimiento de índices.

## Checkpoint 2: Capa de Datos Blindada
- [x] Cero sobreescrituras destructivas con archivos locales viejos.
- [x] Cada modificación se guarda como un elemento independiente en la Lista de SharePoint (sin errores 423 de archivo bloqueado).

---

## Fase 3: Protección de la Interfaz de Usuario y Flujo de Turnos
- [x] **Tarea 3.1**: En `ui_dialogs.py`, deshabilitar la opción de borrar turnos base del maestro para que nunca se pierdan datos.
- [x] **Tarea 3.2**: Corregir el bug de contraparte en "Cambio de turno" (buscar a la contraparte en su fecha correspondiente de la secuencia opuesta, no en la fecha actual).
- [x] **Tarea 3.3**: Proteger la función de duplicar para que solo aplique adiciones sin borrados masivos.

## Checkpoint Final
- [x] Compilación limpia de todos los módulos Python (`py_compile`).
- [x] Suite de pruebas automatizadas integradas completada exitosamente.
