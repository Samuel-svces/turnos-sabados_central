"""
cuadricula_turnos.py
--------------------
Componente de interfaz para la renderización de la cuadrícula de sábados.
Soporta:
  - Modo Administrador: Navegación de semanas, edición interactiva de turnos por modal,
    filtrado y ordenamiento por columna, adición de médicos y duplicación de programación anterior.
  - Modo Público: Visualización limpia de sólo lectura, filtrado por clasificación,
    filtrado/orden por columna, indicadores de observación y tooltips detallados.
"""

import streamlit as st
import pandas as pd
import datetime
from modulos import procesador_datos as dp
from componentes import dialogos


# ---------------------------------------------------------------------------
# Filtro y orden por columna (estilo Excel)
# ---------------------------------------------------------------------------
ORDEN_ETIQUETAS = {"natural": "Natural", "asc": "A → Z", "desc": "Z → A"}
ORDEN_VALORES = {v: k for k, v in ORDEN_ETIQUETAS.items()}


def _init_estado_columnas():
    """Inicializa el estado compartido de orden, filtro y panel por sábado."""
    if 'column_sorts' not in st.session_state:
        st.session_state.column_sorts = {}
    if 'column_filters' not in st.session_state:
        st.session_state.column_filters = {}
    if 'column_panels' not in st.session_state:
        st.session_state.column_panels = {}


def _nombres_unicos(df_dia: pd.DataFrame) -> list:
    """Nombres únicos y válidos de un sábado conservando el orden original."""
    if df_dia is None or df_dia.empty or 'Supernumerary' not in df_dia.columns:
        return []
    return [n for n in dict.fromkeys(df_dia['Supernumerary'].tolist()) if isinstance(n, str) and n.strip()]


def _seleccion_actual(sat_date, nombres: list) -> set:
    """Nombres visibles según el filtro guardado (None = todos)."""
    seleccion = st.session_state.column_filters.get(sat_date)
    if seleccion is None:
        return set(nombres)
    return set(seleccion) & set(nombres)


def _aplicar_filtro_orden(df_dia: pd.DataFrame, sat_date) -> pd.DataFrame:
    """Aplica el filtro por nombre y el orden guardados para una columna."""
    if df_dia is None or df_dia.empty:
        return df_dia

    nombres = _nombres_unicos(df_dia)
    visibles = _seleccion_actual(sat_date, nombres)
    if visibles != set(nombres):
        df_dia = df_dia[df_dia['Supernumerary'].isin(visibles)]

    orden = st.session_state.column_sorts.get(sat_date, "natural")
    if orden == "asc":
        df_dia = df_dia.assign(_orden=df_dia['Supernumerary'].map(dp.normalize_name_no_accents)).sort_values(by='_orden').drop(columns='_orden')
    elif orden == "desc":
        df_dia = df_dia.assign(_orden=df_dia['Supernumerary'].map(dp.normalize_name_no_accents)).sort_values(by='_orden', ascending=False).drop(columns='_orden')
    return df_dia


def _clave_checkbox(sat_date, prefijo: str, indice: int) -> str:
    return f"filtro_chk_{sat_date}_{prefijo}_{indice}"


def _render_menu_excel(sat_date, nombres: list, prefijo: str, pop_key: str):
    """Renderiza el menú emergente flotante con funciones idénticas a Microsoft Excel."""
    txt_key = f"filtro_txt_{sat_date}_{prefijo}"
    if txt_key not in st.session_state:
        st.session_state[txt_key] = ""

    # Callbacks pre-ejecución para evitar StreamlitAPIException al modificar session_state
    def _cb_ord_asc():
        st.session_state.column_sorts[sat_date] = "asc"
        st.session_state[pop_key] = False

    def _cb_ord_desc():
        st.session_state.column_sorts[sat_date] = "desc"
        st.session_state[pop_key] = False

    def _cb_borrar_filtro():
        st.session_state.column_filters[sat_date] = None
        st.session_state.column_sorts[sat_date] = "natural"
        st.session_state[txt_key] = ""
        for idx in range(len(nombres)):
            st.session_state[_clave_checkbox(sat_date, prefijo, idx)] = True
        st.session_state[pop_key] = False

    def _cb_aplicar():
        marcados = [
            n for n in nombres 
            if st.session_state.get(_clave_checkbox(sat_date, prefijo, nombres.index(n)), False)
        ]

        if not marcados:
            st.session_state[pop_key] = False
            return
        elif set(marcados) >= set(nombres):
            st.session_state.column_filters[sat_date] = None
            for idx, n in enumerate(nombres):
                st.session_state[_clave_checkbox(sat_date, prefijo, idx)] = True
        else:
            st.session_state.column_filters[sat_date] = marcados
            for idx, n in enumerate(nombres):
                st.session_state[_clave_checkbox(sat_date, prefijo, idx)] = (n in marcados)

        st.session_state[txt_key] = ""
        st.session_state[pop_key] = False

    # 1. Acciones superiores de ordenamiento estilo Excel
    st.markdown("<div class='excel-menu-btn'>", unsafe_allow_html=True)
    st.button(
        "Ordenar de A a la Z",
        key=f"btn_ord_asc_{sat_date}_{prefijo}",
        icon=":material/arrow_downward:",
        use_container_width=True,
        on_click=_cb_ord_asc
    )

    st.button(
        "Ordenar de Z a la A",
        key=f"btn_ord_desc_{sat_date}_{prefijo}",
        icon=":material/arrow_upward:",
        use_container_width=True,
        on_click=_cb_ord_desc
    )

    orden_actual = st.session_state.column_sorts.get(sat_date, "natural")
    filtro_actual = st.session_state.column_filters.get(sat_date)
    tiene_filtro = (orden_actual != "natural") or (filtro_actual is not None)

    etiqueta_borrar = f"Borrar filtro de '{sat_date.day} {dp.MONTH_NAMES_SP[sat_date.month]}'"
    st.button(
        etiqueta_borrar,
        key=f"btn_borrar_filtro_{sat_date}_{prefijo}",
        icon=":material/filter_alt_off:",
        use_container_width=True,
        disabled=not tiene_filtro,
        on_click=_cb_borrar_filtro
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='excel-menu-divider' />", unsafe_allow_html=True)

    # Formulario atómico para selección de filtros sin recarga por cada casilla (evita lentitud extrema)
    with st.form(key=f"form_filtro_{sat_date}_{prefijo}", border=False):
        # 2. Buscador interactivo de texto
        consulta = st.text_input(
            "Buscar",
            key=txt_key,
            placeholder="Buscar...",
            label_visibility="collapsed",
        )
        consulta_norm = dp.normalize_name_no_accents(consulta or "").upper().strip()
        filtrados = [n for n in nombres if consulta_norm in dp.normalize_name_no_accents(n).upper()]

        # 3. Checkbox Seleccionar todo
        visibles_guardados = _seleccion_actual(sat_date, nombres)

        # Inicializar estado de checkboxes individuales si aún no existen
        for idx, nombre in enumerate(nombres):
            chk_key = _clave_checkbox(sat_date, prefijo, idx)
            if chk_key not in st.session_state:
                st.session_state[chk_key] = (nombre in visibles_guardados)

        chk_all_key = f"filtro_chk_all_{sat_date}_{prefijo}"
        todos_marcados = all(st.session_state.get(_clave_checkbox(sat_date, prefijo, idx), False) for idx in range(len(nombres))) if nombres else False

        st.checkbox(
            "(Seleccionar todo)",
            value=todos_marcados,
            key=chk_all_key,
        )
        st.markdown("<hr class='excel-menu-divider' style='margin: 0.2rem 0 !important;' />", unsafe_allow_html=True)

        # 4. Lista con scroll de casillas individuales
        if not nombres:
            st.caption("Sin médicos programados.")
        else:
            alto_lista = min(170, max(36, 22 * len(nombres)))
            with st.container(height=alto_lista, border=False):
                for idx, nombre in enumerate(nombres):
                    chk_k = _clave_checkbox(sat_date, prefijo, idx)
                    st.checkbox(nombre, key=chk_k)

        st.markdown("<hr class='excel-menu-divider' />", unsafe_allow_html=True)

        # 5. Botón Aplicar (procesamiento en lote único al confirmar)
        st.markdown("<div class='excel-apply-btn'>", unsafe_allow_html=True)
        ningun_marcado = (len(visibles_guardados) == 0)
        st.form_submit_button(
            "Aplicar",
            key=f"btn_aplicar_{sat_date}_{prefijo}",
            use_container_width=True,
            type="primary",
            disabled=ningun_marcado,
            on_click=_cb_aplicar
        )
        st.markdown("</div>", unsafe_allow_html=True)


def _render_encabezado_columna(sat_date, total: int, visibles: int, es_festivo: bool, prefijo: str, nombres: list):
    """Encabezado de fecha con menú flotante tipo Excel (solo en modo administrador)."""
    texto = f"{sat_date.day} {dp.MONTH_NAMES_SP[sat_date.month]} {sat_date.year}"
    etiqueta_medicos = "Médico" if total == 1 else "Médicos"
    if visibles != total:
        texto += f" ({visibles}/{total} {etiqueta_medicos})"
    else:
        texto += f" ({total} {etiqueta_medicos})"
    if es_festivo:
        texto += " (FESTIVO)"

    orden = st.session_state.column_sorts.get(sat_date, "natural")
    if orden == "asc":
        texto += " ▲"
    elif orden == "desc":
        texto += " ▼"

    st.markdown("<div class='date-header-marker admin-filter-header-marker'></div>", unsafe_allow_html=True)
    pop_key = f"popover_filtro_{sat_date}_{prefijo}"

    def _sync_draft_on_popover_open():
        if st.session_state.get(pop_key):
            visibles_reales = _seleccion_actual(sat_date, nombres)
            for idx, nombre in enumerate(nombres):
                st.session_state[_clave_checkbox(sat_date, prefijo, idx)] = (nombre in visibles_reales)
            chk_all_key = f"filtro_chk_all_{sat_date}_{prefijo}"
            st.session_state[chk_all_key] = (set(visibles_reales) >= set(nombres)) if nombres else True
            txt_key = f"filtro_txt_{sat_date}_{prefijo}"
            st.session_state[txt_key] = ""

    with st.popover(texto, use_container_width=True, key=pop_key, on_change=_sync_draft_on_popover_open):
        _render_menu_excel(sat_date, nombres, prefijo, pop_key)


def _guardar_edicion_rapida(sat_date, name, nueva_clasif, nueva_obs, clasif_actual, obs_actual, row_excel, col_excel, sheet_excel):
    """Guarda modificaciones de clasificación y observación directamente desde el panel adyacente."""
    excel_path = st.session_state.excel_path
    mods_list = []

    # 1. Si antes era cambio de turno y la clasificación cambió, restaurar contraparte
    df_s = st.session_state.shifts_df
    if "Cambio de turno con" in str(clasif_actual) and nueva_clasif != clasif_actual:
        counterpart = str(clasif_actual).replace("Cambio de turno con ", "").strip().upper()
        cp_match = df_s[
            (df_s['Supernumerary'].astype(str).str.strip().str.upper() == counterpart) &
            (df_s['Classification'].str.contains(name, na=False))
        ]
        for _, cp_r in cp_match.iterrows():
            mods_list.append({
                'sheet': cp_r['Sheet'],
                'date': cp_r['Date'],
                'original_name': cp_r['Supernumerary'],
                'new_name': cp_r['Supernumerary'],
                'row': int(cp_r['Excel_Row']),
                'col': int(cp_r['Excel_Col']),
                'type': 'REEMPLAZAR',
                'observaciones': cp_r.get('Observation', ''),
                'clasificacion': 'Secuencia Normal'
            })

    # 2. Registrar modificación del turno
    mods_list.append({
        'sheet': sheet_excel,
        'date': sat_date,
        'original_name': name,
        'new_name': name,
        'row': row_excel,
        'col': col_excel,
        'type': 'REEMPLAZAR',
        'observaciones': nueva_obs.strip(),
        'clasificacion': nueva_clasif
    })

    dp.save_modifications_batch(excel_path, mods_list)

    # 3. Guardar acción en session_state para Deshacer
    st.session_state.last_action = {
        'action': 'REPLACE',
        'excel_path': excel_path,
        'sheet': sheet_excel,
        'row': row_excel,
        'col': col_excel,
        'date': sat_date,
        'old_doc': name,
        'new_doc': name,
        'old_obs': obs_actual,
        'new_obs': nueva_obs.strip(),
        'old_clasif': clasif_actual,
        'new_clasif': nueva_clasif
    }

    # 4. Actualización optimista instantánea en memoria
    try:
        date_check = sat_date if isinstance(sat_date, datetime.date) else pd.to_datetime(sat_date).date()
        df_upd = st.session_state.shifts_df.copy()
        df_dates = pd.to_datetime(df_upd['Date'], errors='coerce').dt.date
        mask = (
            (df_upd['Sheet'] == sheet_excel) &
            (df_upd['Excel_Row'] == row_excel) &
            (df_upd['Excel_Col'] == col_excel) &
            (df_dates == date_check)
        ) if row_excel > 0 and col_excel > 0 else (
            (df_upd['Sheet'] == sheet_excel) &
            (df_dates == date_check) &
            (df_upd['Supernumerary'].astype(str).str.strip().str.upper() == str(name).strip().upper())
        )
        if "Cambio de turno con" in str(clasif_actual) and nueva_clasif != clasif_actual:
            counterpart = str(clasif_actual).replace("Cambio de turno con ", "").strip().upper()
            mask_cp = (
                (df_upd['Supernumerary'].astype(str).str.strip().str.upper() == counterpart) &
                (df_upd['Classification'].str.contains(name, na=False))
            )
            df_upd.loc[mask_cp, 'Classification'] = 'Secuencia Normal'

        df_upd.loc[mask, 'Observation'] = nueva_obs.strip()
        df_upd.loc[mask, 'Classification'] = nueva_clasif
        st.session_state.shifts_df = df_upd
        dp.load_modifications.clear()
    except Exception as e_mem:
        print("Aviso actualizando memoria tras guardar:", e_mem)

    st.rerun()


def _remover_turno_rapido(sat_date, name, clasif_actual, obs_actual, row_excel, col_excel, sheet_excel, scope="SOLO_ESTE"):
    """Elimina el turno delegando a la función centralizada en componentes.dialogos."""
    rem_info = {
        'sat_date': sat_date,
        'name': name,
        'clasif_actual': clasif_actual,
        'obs_actual': obs_actual,
        'row_excel': row_excel,
        'col_excel': col_excel,
        'sheet_excel': sheet_excel,
    }
    dialogos.ejecutar_remocion_turno(rem_info, scope=scope)


def _render_panel_edicion_rapida(sat_date, s_idx, name, shift_obs, clasif, row_excel, col_excel, sheet_excel):
    """Panel compacto adyacente (popover) para editar clasificación, observación y remover turno."""
    st.markdown(f"""
    <div style="margin-bottom: 0.6rem; padding-bottom: 0.4rem; border-bottom: 1px solid #e2e8f0;">
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.95rem; font-weight: 700; color: #17243D; line-height: 1.2;">{name}</div>
        <div style="font-size: 0.78rem; color: #64748b; margin-top: 3px;">📅 {sat_date.strftime('%d/%m/%Y')}</div>
    </div>
    """, unsafe_allow_html=True)

    clasif_options = ["Secuencia Normal", "Compensación / Pago de turno", "Cambio de turno"]
    clasif_idx = 0
    if "Compensación" in str(clasif):
        clasif_idx = 1
    elif "Cambio" in str(clasif):
        clasif_idx = 2

    k_clasif = f"pop_rad_clasif_{sat_date}_{s_idx}"
    k_obs = f"pop_txt_obs_{sat_date}_{s_idx}"
    k_save = f"btn_save_pop_{sat_date}_{s_idx}"
    k_del = f"btn_del_pop_{sat_date}_{s_idx}"

    nueva_clasif = st.radio(
        "Clasificación del turno:",
        clasif_options,
        index=clasif_idx,
        key=k_clasif
    )

    nueva_obs = st.text_input(
        "Observaciones:",
        value=shift_obs,
        key=k_obs,
        placeholder="Observación..."
    )

    st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)
    col_save, col_del = st.columns([1.1, 1.0])
    with col_save:
        if st.button("Guardar", key=k_save, type="primary", use_container_width=True, icon=":material/save:"):
            _guardar_edicion_rapida(
                sat_date=sat_date,
                name=name,
                nueva_clasif=nueva_clasif,
                nueva_obs=nueva_obs,
                clasif_actual=clasif,
                obs_actual=shift_obs,
                row_excel=row_excel,
                col_excel=col_excel,
                sheet_excel=sheet_excel
            )
    with col_del:
        if st.button("Eliminar", key=k_del, type="secondary", use_container_width=True, icon=":material/delete_outline:"):
            st.session_state["modal_remover_turno"] = {
                'sat_date': sat_date,
                'name': name,
                'clasif_actual': clasif,
                'obs_actual': shift_obs,
                'row_excel': row_excel,
                'col_excel': col_excel,
                'sheet_excel': sheet_excel
            }
            st.rerun()



def renderizar_cuadricula(df_shifts: pd.DataFrame, df_super: pd.DataFrame, search_query: str, cargar_datos_fn):
    """
    Renderiza la grilla de turnos de sábados completa según el modo de sesión (Admin o Público).
    """
    # Alertas de confirmación inyectadas desde el nivel superior
    if st.session_state.get("show_delete_success_alert", False):
        deleted_doc = st.session_state.get("deleted_doc_name", "Médico")
        st.components.v1.html(f"""
        <script>
            try {{
                const runSuccessAlert = () => {{
                    window.parent.Swal.fire({{
                        title: "✅ Eliminado",
                        text: "{deleted_doc} fue eliminado correctamente.",
                        icon: "success",
                        draggable: true,
                        confirmButtonColor: '#1a73e8',
                        timer: 1500,
                        timerProgressBar: true
                    }});
                }};
                if (!window.parent.Swal) {{
                    const script = window.parent.document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    script.onload = runSuccessAlert;
                    window.parent.document.head.appendChild(script);
                }} else {{
                    runSuccessAlert();
                }}
            }} catch (e) {{
                console.error("SweetAlert2 delete success injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_delete_success_alert"] = False

    if st.session_state.get("show_add_success_alert", False):
        added_doc = st.session_state.get("added_doc_name", "Médico")
        st.components.v1.html(f"""
        <script>
            try {{
                const runAddSuccessAlert = () => {{
                    window.parent.Swal.fire({{
                        title: "✅ Agregado",
                        text: "{added_doc} fue agregado correctamente.",
                        icon: "success",
                        draggable: true,
                        confirmButtonColor: '#1a73e8',
                        timer: 3500,
                        timerProgressBar: true
                    }});
                }};
                if (!window.parent.Swal) {{
                    const script = window.parent.document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    script.onload = runAddSuccessAlert;
                    window.parent.document.head.appendChild(script);
                }} else {{
                    runAddSuccessAlert();
                }}
            }} catch (e) {{
                console.error("SweetAlert2 add success injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_add_success_alert"] = False

    _init_estado_columnas()

    today = datetime.date.today()
    days_to_sat = (5 - today.weekday()) % 7
    first_sat = today + datetime.timedelta(days=days_to_sat)
    generated_sats = [first_sat + datetime.timedelta(weeks=w) for w in range(52)]
    
    if st.session_state.is_admin:
        db_sats = []
        if not df_shifts.empty and 'Date' in df_shifts.columns:
            db_sats = [d for d in df_shifts['Date'].unique() if isinstance(d, (datetime.date, datetime.datetime))]
            db_sats = [d.date() if isinstance(d, datetime.datetime) else d for d in db_sats]
        all_visible_saturdays = sorted(list(set(db_sats + generated_sats)))
    else:
        db_future_sats = []
        if not df_shifts.empty and 'Date' in df_shifts.columns:
            db_future_sats = [d for d in df_shifts['Date'].unique() if d >= today]
            db_future_sats = [d.date() if isinstance(d, datetime.datetime) else d for d in db_future_sats]
        all_visible_saturdays = sorted(list(set(db_future_sats + generated_sats)))
    
    if not all_visible_saturdays:
        st.info("No se encontraron turnos de sábados programados.")
        return

    if st.session_state.is_admin:
        next_sat_idx = 0
        for idx, sat in enumerate(all_visible_saturdays):
            if sat >= today:
                next_sat_idx = idx
                break
        
        if 'saturday_offset' not in st.session_state:
            st.session_state.saturday_offset = next_sat_idx
        
        if st.session_state.saturday_offset >= len(all_visible_saturdays):
            st.session_state.saturday_offset = max(0, ((len(all_visible_saturdays) - 1) // 4) * 4)
            
        offset = st.session_state.saturday_offset
        saturdays = all_visible_saturdays[offset:offset+4]
        
        col_nav_prev, col_nav_info, col_nav_next = st.columns([1.2, 2, 1.2])
        with col_nav_prev:
            has_prev = offset > 0
            if st.button("Sábados Anteriores", use_container_width=True, disabled=not has_prev, key="btn_admin_sats_anteriores"):
                st.session_state.saturday_offset = max(0, offset - 4)
                st.rerun()
        with col_nav_info:
            start_sat = offset + 1
            end_sat = min(len(all_visible_saturdays), offset + 4)
            st.markdown(f"<div class='sat-nav-info-banner'>Sábados {start_sat} a {end_sat} de {len(all_visible_saturdays)} programados</div>", unsafe_allow_html=True)
        with col_nav_next:
            has_next = offset + 4 < len(all_visible_saturdays)
            if st.button("Siguientes Sábados", use_container_width=True, disabled=not has_next, key="btn_admin_sats_siguientes"):
                st.session_state.saturday_offset = offset + 4
                st.rerun()
    else:
        saturdays = all_visible_saturdays[:4]
        
    month_shifts = df_shifts[df_shifts['Date'].isin(saturdays)] if not df_shifts.empty else pd.DataFrame()
    
    # Pre-cálculo de observaciones personales para acceso O(1) ultra rápido (optimización de renderizado)
    super_obs_dict = {}
    if isinstance(df_super, pd.DataFrame) and not df_super.empty:
        col_n = 'NOMBRES Y APELLIDOS' if 'NOMBRES Y APELLIDOS' in df_super.columns else ('Profesional' if 'Profesional' in df_super.columns else None)
        col_o = 'OBSERVACIONES' if 'OBSERVACIONES' in df_super.columns else ('Observaciones' if 'Observaciones' in df_super.columns else None)
        if col_n and col_o:
            super_obs_dict = dict(zip(
                df_super[col_n].astype(str).str.strip().str.upper(),
                df_super[col_o].fillna('').astype(str).str.strip()
            ))

    if search_query:
        # 1. Buscar en TODOS los turnos (df_shifts)
        all_matches = df_shifts[df_shifts['Supernumerary'].str.upper().str.contains(search_query, na=False)] if not df_shifts.empty else pd.DataFrame()
        filter_val = st.session_state.get("filter_class", "Todos")
        if filter_val != "Todos" and not all_matches.empty and 'Classification' in all_matches.columns:
            all_matches = all_matches[all_matches['Classification'].str.contains(filter_val, na=False, case=False)]
        
        if not all_matches.empty:
            # Encontrado: Si estamos en modo admin y la fecha está fuera de los 4 sábados visibles, navegar a esa página
            if st.session_state.is_admin:
                earliest_sat = all_matches['Date'].min()
                if earliest_sat in all_visible_saturdays:
                    target_idx = all_visible_saturdays.index(earliest_sat)
                    current_offset = st.session_state.get('saturday_offset', 0)
                    if target_idx < current_offset or target_idx >= current_offset + 4:
                        st.session_state.saturday_offset = (target_idx // 4) * 4
                        st.rerun()
        else:
            # En modo admin, si un término completo no existe en ninguna fecha, alertar y limpiar
            if st.session_state.is_admin and len(search_query) >= 3:
                st.session_state["clear_search_flag"] = True
                st.session_state["show_error_alert"] = True
                st.rerun()
    
    if st.session_state.is_admin:
        # Callback para procesar Drag & Drop antes de instanciar widgets
        def _cb_on_drag_drop():
            payload_str = st.session_state.get("bridge_drag_drop_payload", "")
            if payload_str:
                import json
                try:
                    st.session_state["active_drag_drop_payload"] = json.loads(payload_str)
                except Exception as e_json:
                    print("Error deserializando drag drop payload:", e_json)
                st.session_state["bridge_drag_drop_payload"] = ""

        # Puente reactivo oculto para Drag & Drop entre columnas de sábados
        st.markdown("""
        <style>
        div[class*="st-key-bridge_drag_drop_payload"],
        div[class*="st-key-btn_trigger_drag_drop"],
        div[data-testid="stElementContainer"]:has(div[class*="st-key-bridge_drag_drop_payload"]),
        div[data-testid="stElementContainer"]:has(div[class*="st-key-btn_trigger_drag_drop"]),
        .drag-drop-bridge-container {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            min-height: 0px !important;
            max-height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            position: absolute !important;
            left: -9999px !important;
            pointer-events: none !important;
            opacity: 0 !important;
        }
        </style>
        <div class='drag-drop-bridge-container'></div>
        """, unsafe_allow_html=True)
        st.text_input(
            "dd_bridge_input",
            key="bridge_drag_drop_payload",
            on_change=_cb_on_drag_drop,
            label_visibility="collapsed"
        )
        st.button(
            "dd_bridge_btn",
            key="btn_trigger_drag_drop",
            on_click=_cb_on_drag_drop
        )

        # Doble verificación de respaldo: si el payload llegó directo a session_state, procesarlo
        raw_payload = st.session_state.get("bridge_drag_drop_payload", "")
        if raw_payload:
            import json
            try:
                st.session_state["active_drag_drop_payload"] = json.loads(raw_payload)
            except Exception as e_json:
                print("Error deserializando drag drop payload directo:", e_json)
            st.session_state["bridge_drag_drop_payload"] = ""

        # Invocación de diálogos modales en el contenedor raíz principal (evita StreamlitInvalidLayoutContextError)
        if st.session_state.get("active_drag_drop_payload"):
            payload = st.session_state.pop("active_drag_drop_payload")
            dialogos.show_drag_drop_action_dialog(payload, cargar_datos_fn)

        if st.session_state.get("modal_add_action_details"):
            add_info = st.session_state.pop("modal_add_action_details")
            dialogos.show_add_dialog(add_info['sat_date'], add_info['sheet'], cargar_datos_fn)

        if st.session_state.get("modal_remover_turno"):
            rem_info = st.session_state.pop("modal_remover_turno")
            dialogos.show_remover_turno_dialog(rem_info, cargar_datos_fn)

        # VISTA ADMINISTRADOR: Botones interactivos con diálogo de edición
        st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
        st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
        cols = st.columns(len(saturdays))
        for idx, sat_date in enumerate(saturdays):
            with cols[idx]:
                st.markdown(f"<div class='saturday-col-marker' data-sat-date='{sat_date}'></div>", unsafe_allow_html=True)
                is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                
                date_shifts_all = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                num_doctors_all = len(date_shifts_all)
                doc_counts = date_shifts_all['Supernumerary'].value_counts() if not date_shifts_all.empty else pd.Series()
                
                nombres_dia = _nombres_unicos(date_shifts_all)

                # Lista de médicos filtrada y ordenada según el icono de la columna
                date_shifts_loop = _aplicar_filtro_orden(date_shifts_all, sat_date)
                if search_query:
                    date_shifts_loop = date_shifts_loop[date_shifts_loop['Supernumerary'].str.upper().str.contains(search_query, na=False)]

                _render_encabezado_columna(
                    sat_date, num_doctors_all, len(date_shifts_loop), is_holiday, "admin", nombres_dia
                )
                shifts_records = date_shifts_loop.to_dict('records')
                for s_idx, s_row in enumerate(shifts_records):
                    name = str(s_row.get('Supernumerary', '')).strip()
                    shift_obs = str(s_row.get('Observation', '')) if pd.notna(s_row.get('Observation')) else ''
                    clasif = s_row.get('Classification', 'Secuencia Normal')
                    row_excel = int(s_row.get('Excel_Row', 0))
                    col_excel = int(s_row.get('Excel_Col', 0))
                    sheet_excel = str(s_row.get('Sheet', ''))
                    
                    personal_obs = super_obs_dict.get(name.upper(), "")
                            
                    has_conflict = doc_counts.get(name, 0) > 1
                    
                    display_name = name
                    if has_conflict:
                        display_name += " 🚨(DUPLICADO)"
                    if "Compensación" in str(clasif):
                        display_name += " 🟡(COMP)"
                    elif "Cambio" in str(clasif):
                        display_name += f" 🔄({clasif.split(' con ')[0]})"
                        
                    if search_query and search_query in name.upper():
                        display_name = "🎯 " + display_name
                        
                    if shift_obs or personal_obs:
                        display_name += " 💬"
                        
                    help_lines = []
                    if "Compensación" in str(clasif): help_lines.append("⚠️ Turno de compensación")
                    if clasif and clasif != "Secuencia Normal": help_lines.append(f"ℹ️ {clasif}")
                    if shift_obs: help_lines.append(f"💬 {shift_obs}")
                    if personal_obs: help_lines.append(f"👤 {personal_obs}")
                    
                    help_text = "\n".join(help_lines).strip()
                    
                    st.markdown(f"<div class='doc-admin-card-wrap' data-doc='{name}' data-date='{sat_date}' data-row='{row_excel}' data-col='{col_excel}' data-sheet=\"{sheet_excel}\" data-clasif=\"{clasif}\"></div>", unsafe_allow_html=True)
                    pop_turn_key = f"pop_turno_{sat_date}_{s_idx}"
                    with st.popover(display_name, use_container_width=True, key=pop_turn_key, help=help_text if help_text else None):
                        _render_panel_edicion_rapida(
                            sat_date=sat_date,
                            s_idx=s_idx,
                            name=name,
                            shift_obs=shift_obs,
                            clasif=clasif,
                            row_excel=row_excel,
                            col_excel=col_excel,
                            sheet_excel=sheet_excel
                        )
                    
                st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
                
                # 1. Botón Agregar Médico
                sheet_name = date_shifts_all.iloc[0]['Sheet'] if not date_shifts_all.empty else f"SABADOS {sat_date.year}"
                if st.button("Agregar Médico", key=f"btn_agregar_medico_{sat_date}", use_container_width=True, type="primary", icon=":material/person_add:"):
                    st.session_state["modal_add_action_details"] = {
                        'sat_date': sat_date,
                        'sheet': sheet_name
                    }
                    st.rerun()
                    
                # 2. Botón Duplicar (si existen turnos anteriores)
                two_weeks_ago = sat_date - datetime.timedelta(weeks=2)
                prev_shifts = df_shifts[df_shifts['Date'] == two_weeks_ago] if not df_shifts.empty else pd.DataFrame()
                if not prev_shifts.empty:
                    st.markdown("<div class='dup-btn-wrapper'></div>", unsafe_allow_html=True)
                    label_dup = f"Duplicar del {two_weeks_ago.day} {dp.MONTH_NAMES_SP[two_weeks_ago.month]}"
                    if st.button(label_dup, key=f"btn_duplicar_{sat_date}", use_container_width=True):
                        with st.spinner("Duplicando..."):
                            try:
                                target_sheet = date_shifts_all.iloc[0]['Sheet'] if not date_shifts_all.empty else f"SABADOS {sat_date.year}"
                                
                                shifts_to_delete_list = []
                                if not date_shifts_all.empty:
                                    for _, row_to_del in date_shifts_all.iterrows():
                                        clasif_dest = str(row_to_del.get('Classification', 'Secuencia Normal'))
                                        if "Compensación" in clasif_dest or "Cambio" in clasif_dest:
                                            continue
                                        shifts_to_delete_list.append({
                                            'sheet': row_to_del['Sheet'],
                                            'doctor': row_to_del['Supernumerary'],
                                            'row': int(row_to_del['Excel_Row']),
                                            'col': int(row_to_del['Excel_Col'])
                                        })
                                        
                                shifts_to_add_list = []
                                for _, row_to_copy in prev_shifts.iterrows():
                                    clasif_orig = str(row_to_copy.get('Classification', 'Secuencia Normal'))
                                    if "Compensación" in clasif_orig or "Cambio" in clasif_orig:
                                        continue
                                    shifts_to_add_list.append({
                                        'doctor': row_to_copy['Supernumerary'],
                                        'observation': row_to_copy.get('Observation', ''),
                                        'classification': row_to_copy.get('Classification', 'Secuencia Normal')
                                    })
                                    
                                dp.duplicate_schedule_batch(
                                    excel_path=st.session_state.excel_path,
                                    target_sheet=target_sheet,
                                    target_date=sat_date,
                                    shifts_to_delete_list=shifts_to_delete_list,
                                    shifts_to_add_list=shifts_to_add_list
                                )

                                # Actualización optimista instantánea en memoria (evita recarga síncrona de SharePoint)
                                try:
                                    df_upd = st.session_state.shifts_df.copy() if not st.session_state.shifts_df.empty else pd.DataFrame()
                                    if not df_upd.empty:
                                        date_check = sat_date if isinstance(sat_date, datetime.date) else pd.to_datetime(sat_date).date()
                                        df_dates = pd.to_datetime(df_upd['Date'], errors='coerce').dt.date
                                        mask_date = (df_dates == date_check)
                                        # Conservar solo los turnos condicionales (Compensación/Cambio) del día destino
                                        cond_mask = df_upd['Classification'].astype(str).str.contains('Compensación|Cambio', na=False, regex=True)
                                        df_upd = df_upd[~mask_date | cond_mask]
                                    new_rows = []
                                    for item in shifts_to_add_list:
                                        new_rows.append({
                                            'Sheet': target_sheet,
                                            'Month_Header': dp.MONTH_NAMES_SP.get(sat_date.month, 'EXTRA'),
                                            'Date': sat_date,
                                            'Year': sat_date.year,
                                            'Month': sat_date.month,
                                            'Supernumerary': str(item['doctor']).strip().upper(),
                                            'Excel_Row': 0,
                                            'Excel_Col': 0,
                                            'Header_Row': 0,
                                            'Observation': str(item.get('observation', '')).strip(),
                                            'Classification': str(item.get('classification', 'Secuencia Normal')).strip()
                                        })
                                    if new_rows:
                                        st.session_state.shifts_df = pd.concat(
                                            [df_upd, pd.DataFrame(new_rows)], ignore_index=True
                                        )
                                    else:
                                        st.session_state.shifts_df = df_upd
                                    dp.load_modifications.clear()
                                except Exception as e_mem:
                                    print("Aviso actualizando memoria tras duplicar:", e_mem)
                                    cargar_datos_fn()

                                st.success(f"Programación duplicada del {two_weeks_ago.day} de {dp.MONTH_NAMES_SP[two_weeks_ago.month]}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al duplicar: {e}")
                                
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # VISTA PÚBLICA: Cuadrícula limpia de solo lectura
        with st.container():
            st.markdown("<div class='columns-card-marker'></div>", unsafe_allow_html=True)
            st.markdown("<div class='calendar-grid'>", unsafe_allow_html=True)
            cols = st.columns(len(saturdays))
            for idx, sat_date in enumerate(saturdays):
                with cols[idx]:
                    st.markdown("<div class='saturday-col-marker'></div>", unsafe_allow_html=True)
                    is_holiday = sat_date.month == 12 and sat_date.day in [24, 31]
                    
                    date_shifts_all = month_shifts[month_shifts['Date'] == sat_date] if not month_shifts.empty else pd.DataFrame()
                    num_doctors_all = len(date_shifts_all)
                    
                    date_shifts = date_shifts_all.copy()
                    filter_val = st.session_state.get("filter_class", "Todos")
                    if filter_val != "Todos":
                        date_shifts = date_shifts[date_shifts['Classification'].str.contains(filter_val, na=False, case=False)]
                    
                    sort_type = st.session_state.column_sorts.get(sat_date, "natural")

                    texto_header = f"{sat_date.day} {dp.MONTH_NAMES_SP[sat_date.month]} {sat_date.year}"
                    etiqueta_medicos = "Médico" if num_doctors_all == 1 else "Médicos"
                    texto_header += f" ({num_doctors_all} {etiqueta_medicos})"
                    if is_holiday:
                        texto_header += " (FESTIVO)"
                    if sort_type == "asc":
                        texto_header += " 🔤"

                    st.markdown("<div class='date-header-marker sat-header-pub-marker'></div>", unsafe_allow_html=True)
                    if st.button(texto_header, key=f"btn_ordenar_pub_{sat_date}", use_container_width=True):
                        st.session_state.column_sorts[sat_date] = "natural" if sort_type == "asc" else "asc"
                        st.rerun()

                    # Lista de médicos en modo usuario: ordenada de la A a la Z si sort_type es 'asc', o natural
                    if sort_type == "asc":
                        date_shifts_loop = date_shifts.assign(
                            _orden=date_shifts['Supernumerary'].map(dp.normalize_name_no_accents)
                        ).sort_values(by='_orden').drop(columns='_orden')
                    else:
                        date_shifts_loop = date_shifts

                    if search_query:
                        date_shifts_loop = date_shifts_loop[date_shifts_loop['Supernumerary'].str.upper().str.contains(search_query, na=False)]
                    pub_records = date_shifts_loop.to_dict('records')
                    for s_row in pub_records:
                        name = str(s_row.get('Supernumerary', '')).strip()
                        shift_obs = str(s_row.get('Observation', '')) if pd.notna(s_row.get('Observation')) else ''
                        clasif = s_row.get('Classification', 'Secuencia Normal')
                        is_compensation = "Compensación" in str(clasif)
                        
                        personal_obs = super_obs_dict.get(name.upper(), "")
                                
                        has_obs = (clasif and clasif != "Secuencia Normal") or shift_obs or personal_obs
                        help_lines = []
                        if is_compensation: help_lines.append("⚠️ Turno de compensación")
                        if clasif and clasif != "Secuencia Normal": help_lines.append(f"ℹ️ {clasif}")
                        if shift_obs: help_lines.append(f"💬 {shift_obs}")
                        if personal_obs: help_lines.append(f"👤 {personal_obs}")
                        
                        help_text = "<br>".join(help_lines).strip()
                        badge_classes = "doc-name-badge" + (" has-obs" if has_obs else "")
                        if search_query and search_query in name.upper():
                            badge_classes += " search-highlight"
                            
                        obs_dot = "<span class='obs-dot'></span>" if has_obs else ""
                        tooltip_html = f"<div class='doc-obs-tooltip'>{help_text}</div>" if help_text else ""
                        
                        display_name = name
                        if "Cambio" in str(clasif):
                            display_name += f" ({clasif})"
                        
                        st.markdown(f"<div class='doc-btn-wrap' data-doc='{name}'><div class='{badge_classes}'>{obs_dot}{display_name}</div>{tooltip_html}</div>", unsafe_allow_html=True)
                        
            st.markdown("</div>", unsafe_allow_html=True)
