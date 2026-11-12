"""
buscador.py
-----------
Componente de búsqueda reactiva en vivo y filtros de clasificación de turnos.
Centra el input de búsqueda en pantalla, elimina los botones manuales y aplica
un subrayado y resaltado dinámico en tiempo real letra por letra sin requerir Enter.
"""

import streamlit as st
import datetime
from modulos import procesador_datos as dp


def _ejecutar_deshacer(cargar_datos_fn=None):
    """Revierte la última acción realizada por el administrador."""
    la = st.session_state.get('last_action')
    if not (isinstance(la, dict) and bool(la)):
        return
    try:
        accion = str(la.get('action', ''))
        excel_p = str(la.get('excel_path', ''))
        hoja = str(la.get('sheet', ''))
        fecha = la.get('date')
        medico = str(la.get('doc', ''))
        obs = str(la.get('obs', ''))
        clasif = str(la.get('clasificacion', 'Secuencia Normal'))

        if accion in ['ELIMINAR', 'ELIMINAR_SIMPLE']:
            dp.add_shift_to_date(excel_p, hoja, fecha, medico, obs, clasif)
            st.success("Acción revertida: Médico re-agregado.")
        elif accion == 'ELIMINAR_LOTE':
            shifts_to_restore = []
            for item in la.get('deleted_items', []):
                if isinstance(item, dict):
                    shifts_to_restore.append({
                        'sheet': item.get('sheet'),
                        'date': item.get('date'),
                        'doc': item.get('doc'),
                        'obs': item.get('obs'),
                        'clasificacion': item.get('clasificacion')
                    })
            dp.add_shifts_batch(excel_p, shifts_to_restore)
            st.success(f"Acción revertida: {len(shifts_to_restore)} asignaciones de turnos restauradas.")
        elif accion == 'AGREGAR':
            dp.delete_shift_cell(excel_p, hoja, 0, 0, fecha, "", medico, clasif)
            st.success("Acción revertida: Médico eliminado del día.")
        elif accion == 'MOVE':
            nueva_fecha = la.get('new_date')
            fecha_anterior = la.get('old_date')
            dp.delete_shift_cell(excel_p, hoja, 0, 0, nueva_fecha, "", medico, clasif)
            dp.add_shift_to_date(excel_p, hoja, fecha_anterior, medico, obs, clasif)
            st.success("Acción revertida: Movimiento cancelado.")
        elif accion == 'REPLACE':
            dp.update_shift_cell(
                excel_path=excel_p,
                sheet_name=hoja,
                row_idx=int(la.get('row', 0)),
                col_idx=int(la.get('col', 0)),
                new_name=str(la.get('old_doc', '')),
                date_val=fecha,
                observation=str(la.get('old_obs', '')),
                original_name=str(la.get('new_doc', '')),
                clasificacion=str(la.get('old_clasif', 'Secuencia Normal'))
            )
            st.success("Acción revertida: Reemplazo / edición cancelado.")

        st.session_state.last_action = None
        if callable(cargar_datos_fn):
            cargar_datos_fn()
        st.rerun()
    except Exception as e:
        st.error(f"No se pudo deshacer: {e}")


def renderizar_buscador(cargar_datos_fn=None):
    """
    Renderiza el buscador reactivo centrado y los filtros dinámicos por clasificación.
    En modo administrador con última acción, ubica el botón estético de deshacer al lado de la barra de búsqueda.
    Retorna:
        search_query (str): Término de búsqueda en mayúsculas (si se completó con Enter o estado previo).
        filtro_clasificacion (str): Filtro activo ('Todos', 'Secuencia Normal', 'Compensación').
    """
    if "input_busqueda_medico" not in st.session_state:
        st.session_state["input_busqueda_medico"] = ""

    if st.session_state.get("clear_search_flag", False):
        st.session_state["input_busqueda_medico"] = ""
        st.session_state["clear_search_flag"] = False

    la = st.session_state.get('last_action')
    tiene_deshacer = bool(st.session_state.get('is_admin') and isinstance(la, dict) and bool(la))

    # Fila de Buscador Centrado en Pantalla con botón Deshacer al lado si aplica
    col_spacer_l, col_search_center, col_spacer_r = st.columns([1.5, 3.0, 1.5])
    with col_search_center:
        st.markdown("<div class='custom-search-marker'></div>", unsafe_allow_html=True)
        if tiene_deshacer:
            col_search_input, col_undo_btn = st.columns([0.87, 0.13], vertical_alignment="center")
            with col_search_input:
                search_query = st.text_input(
                    "Buscador", 
                    key="input_busqueda_medico", 
                    placeholder="", 
                    label_visibility="collapsed"
                ).strip().upper()
            with col_undo_btn:
                if st.button(" ", key="btn_deshacer_ultimo_cambio", help="Deshacer último movimiento"):
                    _ejecutar_deshacer(cargar_datos_fn)
        else:
            search_query = st.text_input(
                "Buscador", 
                key="input_busqueda_medico", 
                placeholder="", 
                label_visibility="collapsed"
            ).strip().upper()

    # Estado para el filtro de clasificación (por defecto Todos)
    st.session_state["filter_class"] = "Todos"

    # Inyección de script reactivo en tiempo real para filtrar y resaltar con cada pulsación de tecla
    st.components.v1.html(r"""
    <script>
    const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;

    function normalizarTexto(txt) {
        return (txt || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim()
            .toUpperCase();
    }

    // Controles del filtro/orden por columna: no se ocultan ni se estilizan como médicos
    function esControlFiltro(el) {
        if (!el || !el.closest) return false;
        if (el.closest('[class*="st-key-popover_filtro"]')) return true;
        if (el.closest('[data-testid="stPopoverBody"]')) return true;
        if (el.closest('[data-testid="stVerticalBlockBorderWrapper"]')) return true;
        if (el.closest('.excel-menu-btn') || el.closest('.excel-apply-btn')) return true;
        const txt = (el.innerText || el.textContent || "").trim();
        return txt === "Filtrar" || txt === "Todos" || txt === "Ninguno" || txt === "Limpiar filtro" || txt === "Aplicar" || txt.startsWith("Ordenar") || txt.startsWith("Borrar filtro");
    }

    function aplicarResaltadoEnVivo(termino) {
        const parentDoc = window.parent.document;
        const cleanTerm = normalizarTexto(termino);
        
        // Columnas de sábados
        const cols = parentDoc.querySelectorAll('div[data-testid="stColumn"]:has(.saturday-col-marker), div[data-testid="column"]:has(.saturday-col-marker)');

        cols.forEach(col => {
            // MODO ADMINISTRADOR: Filtrado de tarjetas de turno a través de metadatos rápidos
            const cardWraps = col.querySelectorAll('.doc-admin-card-wrap');
            cardWraps.forEach(wrap => {
                const docName = normalizarTexto(wrap.getAttribute('data-doc') || '');
                const metaContainer = wrap.closest('div[data-testid="stElementContainer"]') || wrap.parentElement;
                let cardContainer = metaContainer ? metaContainer.nextElementSibling : null;
                if (cardContainer && !cardContainer.querySelector('button') && cardContainer.nextElementSibling) {
                    cardContainer = cardContainer.nextElementSibling;
                }
                if (!cardContainer) return;
                const btn = cardContainer.querySelector('button');

                if (!cleanTerm) {
                    cardContainer.classList.remove('search-card-hidden');
                    cardContainer.style.removeProperty('display');
                    if (btn) btn.classList.remove('search-highlight-active', 'search-dimmed');
                    return;
                }

                if (docName.includes(cleanTerm)) {
                    cardContainer.classList.remove('search-card-hidden');
                    cardContainer.style.removeProperty('display');
                    if (btn) {
                        btn.classList.remove('search-dimmed');
                        btn.classList.add('search-highlight-active');
                    }
                } else {
                    cardContainer.classList.add('search-card-hidden');
                    cardContainer.style.setProperty('display', 'none', 'important');
                    if (btn) {
                        btn.classList.remove('search-highlight-active');
                        btn.classList.add('search-dimmed');
                    }
                }
            });

            // Ocultar botones de acción en búsqueda activa
            const actionBtns = col.querySelectorAll('button[data-testid*="btn_agregar_medico"], button[data-testid*="btn_duplicar"]');
            actionBtns.forEach(abtn => {
                const acont = abtn.closest('div[data-testid="stElementContainer"]') || abtn.parentElement;
                if (acont) {
                    if (cleanTerm) {
                        acont.style.setProperty('display', 'none', 'important');
                    } else {
                        acont.style.removeProperty('display');
                    }
                }
            });

            // MODO PÚBLICO: Badges (.doc-btn-wrap)
            const docWraps = col.querySelectorAll('.doc-btn-wrap');
            docWraps.forEach(wrap => {
                const docText = normalizarTexto(wrap.getAttribute('data-doc') || wrap.textContent || '');
                const cont = wrap.closest('div[data-testid="stElementContainer"]') || wrap;
                const badge = wrap.querySelector('.doc-name-badge') || wrap;

                if (!cleanTerm) {
                    if (cont) {
                        cont.classList.remove('search-card-hidden');
                        cont.style.removeProperty('display');
                    }
                    badge.classList.remove('search-highlight-active', 'search-dimmed');
                    return;
                }

                if (docText.includes(cleanTerm)) {
                    if (cont) {
                        cont.classList.remove('search-card-hidden');
                        cont.style.removeProperty('display');
                    }
                    badge.classList.remove('search-dimmed');
                    badge.classList.add('search-highlight-active');
                } else {
                    if (cont) {
                        cont.classList.add('search-card-hidden');
                        cont.style.setProperty('display', 'none', 'important');
                    }
                    badge.classList.remove('search-highlight-active');
                    badge.classList.add('search-dimmed');
                }
            });
        });
    }

    const aplicarBusquedaEnVivo = aplicarResaltadoEnVivo;

    let searchDebounceTimer = null;
    let rafSearchId = null;
    let lastSyncedVal = null;
    let isSyncingSearch = false;

    function sincronizarBusquedaConStreamlit(val) {
        if (isSyncingSearch) return;
        const parentDoc = window.parent.document;
        const clean = (val || "").trim();
        if (clean === lastSyncedVal) return;
        lastSyncedVal = clean;

        let inputEl = parentDoc.querySelector('input[aria-label="Buscador"], div[data-testid="stTextInput"] input');
        if (!inputEl) return;

        isSyncingSearch = true;
        try {
            // Sincronizar el valor hacia el componente React de Streamlit
            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeSetter.call(inputEl, clean);
            inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            inputEl.dispatchEvent(new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13
            }));
        } catch (e) {
            console.error("Error al sincronizar buscador:", e);
        } finally {
            setTimeout(() => { isSyncingSearch = false; }, 300);
        }
    }

    function vincularBuscadorReactivo() {
        const parentDoc = window.parent.document;
        const marker = parentDoc.querySelector('.custom-search-marker');
        let inputBuscador = null;
        if (marker) {
            const col = marker.closest('[data-testid="stColumn"], [data-testid="column"], .stColumn');
            if (col) {
                inputBuscador = col.querySelector('input');
            }
        }
        if (!inputBuscador) {
            inputBuscador = parentDoc.querySelector('input[aria-label="Buscador"], div[data-testid="stTextInput"] input');
        }
        if (!inputBuscador) return false;

        inputBuscador.placeholder = "";
        inputBuscador.setAttribute("placeholder", "");
        inputBuscador.setAttribute("autocomplete", "off");
        inputBuscador.setAttribute("autocorrect", "off");
        inputBuscador.setAttribute("autocapitalize", "off");
        inputBuscador.setAttribute("spellcheck", "false");
        inputBuscador.setAttribute("name", "filtro_vivo_medicos");

        const containerInput = inputBuscador.closest('div[data-testid="stTextInput"]');
        if (containerInput) {
            const tooltips = containerInput.querySelectorAll('[data-testid="stTextInputInstructions"], [data-testid="InputInstructions"], .stTextInputInstructions');
            tooltips.forEach(t => t.style.setProperty('display', 'none', 'important'));
        }

        if (!inputBuscador.dataset.liveSearchBound) {
            inputBuscador.dataset.liveSearchBound = "true";
            
            // 1. Filtrado instantáneo a 60fps con requestAnimationFrame (0ms de retraso al teclear)
            inputBuscador.addEventListener('input', (e) => {
                if (isSyncingSearch) return;
                const val = e.target.value;
                if (rafSearchId) cancelAnimationFrame(rafSearchId);
                rafSearchId = requestAnimationFrame(() => {
                    aplicarBusquedaEnVivo(val);
                });

                // 2. Sincronización con el servidor Streamlit solo tras pausa prolongada (1200ms)
                // para que NUNCA interrumpa ni bloquee mientras el usuario está escribiendo
                if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
                const debounceMs = val.length === 0 ? 300 : 1200;
                searchDebounceTimer = setTimeout(() => {
                    sincronizarBusquedaConStreamlit(val);
                }, debounceMs);
            });

            inputBuscador.addEventListener('focus', () => {
                if (inputBuscador.value) aplicarBusquedaEnVivo(inputBuscador.value);
            });

            inputBuscador.addEventListener('paste', () => {
                setTimeout(() => {
                    aplicarBusquedaEnVivo(inputBuscador.value);
                    sincronizarBusquedaConStreamlit(inputBuscador.value);
                }, 20);
            });

            inputBuscador.addEventListener('keydown', (e) => {
                if (e.key === "Enter") {
                    if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
                    sincronizarBusquedaConStreamlit(e.target.value);
                } else if (e.key === "Escape") {
                    inputBuscador.value = "";
                    aplicarBusquedaEnVivo("");
                    if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
                    sincronizarBusquedaConStreamlit("");
                }
            });
        }

        if (inputBuscador.value) {
            aplicarBusquedaEnVivo(inputBuscador.value);
        }
        return true;
    }

    function sonMismaSecuencia(fechaStr1, fechaStr2) {
        if (!fechaStr1 || !fechaStr2) return false;
        try {
            const d1 = new Date(fechaStr1 + 'T00:00:00');
            const d2 = new Date(fechaStr2 + 'T00:00:00');
            const diffTime = Math.abs(d2.getTime() - d1.getTime());
            const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
            return (diffDays % 14) === 0;
        } catch (e) {
            return false;
        }
    }

    function mostrarIndicadorCargaPanel() {
        const parentDoc = window.parent.document;
        let pill = parentDoc.querySelector('.drag-drop-loading-pill');
        if (!pill) {
            pill = parentDoc.createElement('div');
            pill.className = 'drag-drop-loading-pill';
            pill.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f9a9b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="animation: spinPill 0.8s linear infinite;">
                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                    <path d="M12 2a10 10 0 0 1 10 10"></path>
                </svg>
                <span>Abriendo panel de traslado...</span>
                <style>
                    @keyframes spinPill { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
                </style>
            `;
            parentDoc.body.appendChild(pill);
        }
        setTimeout(() => {
            if (pill && pill.parentNode) pill.parentNode.removeChild(pill);
        }, 1800);
    }

    function vincularFiltrosExcel() {
        const parentDoc = window.parent.document;
        const popovers = parentDoc.querySelectorAll('[data-testid="stPopoverBody"]');
        if (!popovers || popovers.length === 0) return;

        popovers.forEach(popover => {
            const applyWrapper = popover.querySelector('.excel-apply-btn, div[class*="st-key-btn_aplicar"]');
            const searchInput = popover.querySelector('input[placeholder="Buscar..."]');
            if (!applyWrapper && !searchInput) return;

            const applyBtn = popover.querySelector('.excel-apply-btn button, div[class*="st-key-btn_aplicar"] button, button[data-testid="stBaseButton-primary"]');

            // 1. Función para refrescar si el botón 'Aplicar' debe estar habilitado o deshabilitado
            function refrescarEstadoAplicar() {
                const applyBtn = popover.querySelector('.excel-apply-btn button, div[class*="st-key-btn_aplicar"] button, button[data-testid="stBaseButton-primary"]');
                if (!applyBtn) return;
                const doctorCheckboxes = popover.querySelectorAll('[data-testid="stCheckbox"]');
                let countChecked = 0;
                doctorCheckboxes.forEach((chk, idx) => {
                    if (idx === 0 || chk.textContent.includes("Seleccionar")) return;
                    const inp = chk.querySelector('input[type="checkbox"]');
                    if (inp && inp.checked) countChecked++;
                });

                if (countChecked === 0) {
                    applyBtn.disabled = true;
                    applyBtn.setAttribute("disabled", "true");
                    applyBtn.classList.add("btn-aplicar-deshabilitado");
                } else {
                    applyBtn.disabled = false;
                    applyBtn.removeAttribute("disabled");
                    applyBtn.classList.remove("btn-aplicar-deshabilitado");
                }
            }

            // 2. Función robusta para cambiar el estado de un checkbox en Streamlit BaseWeb
            function forzarEstadoCheckbox(chkCont, targetChecked) {
                const inp = chkCont.querySelector('input[type="checkbox"]');
                if (!inp) return;
                if (inp.checked === targetChecked) return;

                const label = chkCont.querySelector('label') || chkCont;

                // 1. Simular click directo sobre el elemento label (dispara el SyntheticEvent oficial de BaseWeb / React)
                label.click();

                // 2. Verificación y respaldo a bajo nivel si el click no conmutó el estado
                if (inp.checked !== targetChecked) {
                    try {
                        const ownerWin = inp.ownerDocument.defaultView || window.parent || window;
                        const setter = Object.getOwnPropertyDescriptor(ownerWin.HTMLInputElement.prototype, "checked")?.set;
                        if (setter) setter.call(inp, targetChecked);
                        else inp.checked = targetChecked;
                        if (inp._valueTracker) inp._valueTracker.setValue(!targetChecked);
                        inp.dispatchEvent(new ownerWin.Event('input', { bubbles: true, cancelable: true }));
                        inp.dispatchEvent(new ownerWin.Event('change', { bubbles: true, cancelable: true }));
                    } catch (err) {
                        console.error("Error al forzar checkbox:", err);
                    }
                }

                // 3. Sincronización visual forzada de atributos BaseWeb
                try {
                    inp.setAttribute('aria-checked', targetChecked ? 'true' : 'false');
                    const baseBox = chkCont.querySelector('[data-baseweb="checkbox"]');
                    if (baseBox) {
                        baseBox.setAttribute('aria-checked', targetChecked ? 'true' : 'false');
                    }
                } catch (e) {}
            }

            // 3. Vincular buscador reactivo dentro del popover
            if (searchInput && !searchInput.dataset.excelFilterBound) {
                searchInput.dataset.excelFilterBound = "true";
                searchInput.setAttribute("autocomplete", "off");
                searchInput.setAttribute("autocorrect", "off");
                searchInput.setAttribute("autocapitalize", "off");
                searchInput.setAttribute("spellcheck", "false");

                searchInput.addEventListener('input', (e) => {
                    const query = normalizarTexto(e.target.value);
                    const chks = popover.querySelectorAll('[data-testid="stCheckbox"]');
                    let visibles = 0;
                    chks.forEach((chk, idx) => {
                        if (idx === 0 || chk.textContent.includes("Seleccionar")) return;
                        const txt = normalizarTexto(chk.textContent);
                        const cont = chk.closest('div[data-testid="stElementContainer"]') || chk;
                        if (!query || txt.includes(query)) {
                            cont.style.removeProperty('display');
                            visibles++;
                        } else {
                            cont.style.setProperty('display', 'none', 'important');
                        }
                    });

                    let msgEl = popover.querySelector('.excel-no-match-alert');
                    if (query && visibles === 0) {
                        if (!msgEl) {
                            msgEl = parentDoc.createElement('div');
                            msgEl.className = 'excel-no-match-alert';
                            msgEl.textContent = 'Sin coincidencias.';
                            msgEl.style.cssText = 'color: #64748b; font-size: 0.78rem; padding: 0.35rem 0.2rem; text-align: center; font-style: italic;';
                            const scrollCont = popover.querySelector('[data-testid="stVerticalBlock"]');
                            if (scrollCont) scrollCont.appendChild(msgEl);
                        }
                        msgEl.style.removeProperty('display');
                    } else if (msgEl) {
                        msgEl.style.setProperty('display', 'none', 'important');
                    }

                    // Sincronizar estado del botón aplicar según lo que haya seleccionado
                    refrescarEstadoAplicar();
                });

                searchInput.addEventListener('keydown', (e) => {
                    if (e.key === "Enter") {
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    } else if (e.key === "Escape") {
                        searchInput.value = "";
                        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                });
            }

            let isBatchUpdating = false;

            // 4. Vincular checkbox (Seleccionar todo) con selección/deselección en cascada y deshabilitación
            const allCheckboxes = popover.querySelectorAll('[data-testid="stCheckbox"]');
            if (allCheckboxes.length > 0) {
                const selectAllCont = allCheckboxes[0];
                if (selectAllCont.textContent.includes("Seleccionar") && !selectAllCont.dataset.excelSelectAllBound) {
                    selectAllCont.dataset.excelSelectAllBound = "true";
                    const chkAllInput = selectAllCont.querySelector('input[type="checkbox"]');

                    const ejecutarAccionSelectAll = (forzadoTarget) => {
                        if (isBatchUpdating) return;
                        isBatchUpdating = true;
                        try {
                            const targetChecked = (typeof forzadoTarget === 'boolean') ? forzadoTarget : (chkAllInput ? chkAllInput.checked : false);
                            const doctorCheckboxes = popover.querySelectorAll('[data-testid="stCheckbox"]');
                            doctorCheckboxes.forEach((chk, idx) => {
                                if (idx === 0 || chk.textContent.includes("Seleccionar")) return;
                                const cont = chk.closest('div[data-testid="stElementContainer"]') || chk;
                                if (cont.style.display !== 'none') {
                                    forzarEstadoCheckbox(chk, targetChecked);
                                }
                            });
                            refrescarEstadoAplicar();
                        } finally {
                            setTimeout(() => { isBatchUpdating = false; }, 80);
                        }
                    };

                    if (chkAllInput) {
                        chkAllInput.addEventListener('change', (e) => {
                            ejecutarAccionSelectAll(e.target.checked);
                        });
                    }
                    selectAllCont.addEventListener('click', () => {
                        setTimeout(() => {
                            if (!isBatchUpdating && chkAllInput) {
                                ejecutarAccionSelectAll(chkAllInput.checked);
                            }
                        }, 15);
                    });
                }
            }

            // 5. Vincular casillas individuales de médicos para refrescar botón y checkbox general
            allCheckboxes.forEach((chk, idx) => {
                if (idx === 0 || chk.textContent.includes("Seleccionar")) return;
                if (chk.dataset.docChkBound) return;
                chk.dataset.docChkBound = "true";

                const docInp = chk.querySelector('input[type="checkbox"]');
                const onDoctorToggle = () => {
                    if (isBatchUpdating) return;
                    setTimeout(() => {
                        if (isBatchUpdating) return;
                        refrescarEstadoAplicar();

                        // Actualizar estado de (Seleccionar todo) según los médicos visibles sin bucle recursivo
                        const firstChk = popover.querySelectorAll('[data-testid="stCheckbox"]')[0];
                        if (firstChk && firstChk.textContent.includes("Seleccionar")) {
                            const firstInp = firstChk.querySelector('input[type="checkbox"]');
                            const docChks = popover.querySelectorAll('[data-testid="stCheckbox"]');
                            let totalVis = 0;
                            let checkedVis = 0;
                            docChks.forEach((dchk, didx) => {
                                if (didx === 0 || dchk.textContent.includes("Seleccionar")) return;
                                const cont = dchk.closest('div[data-testid="stElementContainer"]') || dchk;
                                if (cont.style.display !== 'none') {
                                    totalVis++;
                                    const dinp = dchk.querySelector('input[type="checkbox"]');
                                    if (dinp && dinp.checked) checkedVis++;
                                }
                            });
                            const allChecked = totalVis > 0 && (checkedVis === totalVis);
                            if (firstInp && firstInp.checked !== allChecked) {
                                try {
                                    const ownerWin = firstInp.ownerDocument.defaultView || window.parent || window;
                                    const setter = Object.getOwnPropertyDescriptor(ownerWin.HTMLInputElement.prototype, "checked")?.set;
                                    if (setter) setter.call(firstInp, allChecked);
                                    else firstInp.checked = allChecked;
                                    if (firstInp._valueTracker) firstInp._valueTracker.setValue(!allChecked);
                                    firstInp.dispatchEvent(new ownerWin.Event('input', { bubbles: true }));
                                    firstInp.dispatchEvent(new ownerWin.Event('change', { bubbles: true }));
                                    firstInp.setAttribute('aria-checked', allChecked ? 'true' : 'false');
                                    const firstBaseBox = firstChk.querySelector('[data-baseweb="checkbox"]');
                                    if (firstBaseBox) firstBaseBox.setAttribute('aria-checked', allChecked ? 'true' : 'false');
                                } catch (e) {}
                            }
                        }
                    }, 20);
                };

                chk.addEventListener('click', onDoctorToggle);
                if (docInp) docInp.addEventListener('change', onDoctorToggle);
            });

            // 6. Evaluación inicial al abrir o montar el popover
            refrescarEstadoAplicar();
        });
    }

    function inicializarDragAndDrop() {
        const parentDoc = window.parent.document;

        // Ocultar preventivamente los contenedores del puente en el DOM
        const bridgeElements = parentDoc.querySelectorAll('div[class*="st-key-bridge_drag_drop_payload"], div[class*="st-key-btn_trigger_drag_drop"], .drag-drop-bridge-container');
        bridgeElements.forEach(el => {
            el.style.setProperty('display', 'none', 'important');
            const cont = el.closest('div[data-testid="stElementContainer"]');
            if (cont) cont.style.setProperty('display', 'none', 'important');
        });

        const colMarkers = parentDoc.querySelectorAll('div[data-testid="stColumn"]:has(.saturday-col-marker), div[data-testid="column"]:has(.saturday-col-marker)');
        let currentDropCol = null;

        colMarkers.forEach(col => {
            const marker = col.querySelector('.saturday-col-marker');
            const colDate = marker ? marker.getAttribute('data-sat-date') : null;

            // 1. Configurar botones de médicos como arrastrables
            const wraps = col.querySelectorAll('.doc-admin-card-wrap');
            wraps.forEach(wrap => {
                const container = wrap.closest('div[data-testid="stElementContainer"]');
                if (!container) return;
                const nextContainer = container.nextElementSibling;
                const btn = nextContainer ? nextContainer.querySelector('button') : null;
                if (!btn || btn.dataset.dragInitialized) return;

                btn.dataset.dragInitialized = "true";
                btn.setAttribute('draggable', 'true');
                btn.classList.add('doc-draggable-card');

                let isDraggingCard = false;

                btn.addEventListener('dragstart', (e) => {
                    isDraggingCard = true;
                    btn.dataset.isDragging = "true";
                    const data = {
                        doctor: wrap.getAttribute('data-doc'),
                        source_date: wrap.getAttribute('data-date') || colDate,
                        row: parseInt(wrap.getAttribute('data-row') || '0'),
                        col: parseInt(wrap.getAttribute('data-col') || '0'),
                        sheet: wrap.getAttribute('data-sheet'),
                        clasificacion: wrap.getAttribute('data-clasif') || 'Secuencia Normal'
                    };
                    e.dataTransfer.setData('text/plain', JSON.stringify(data));
                    e.dataTransfer.effectAllowed = 'move';
                    btn.classList.add('doc-card-dragging');

                    colMarkers.forEach(targetCol => {
                        const targetMarker = targetCol.querySelector('.saturday-col-marker');
                        const targetDate = targetMarker ? targetMarker.getAttribute('data-sat-date') : null;
                        if (targetDate && targetDate !== data.source_date) {
                            if (sonMismaSecuencia(data.source_date, targetDate)) {
                                targetCol.classList.add('saturday-col-blocked-sequence');
                            } else {
                                targetCol.classList.add('saturday-col-droppable-hint');
                            }
                        }
                    });
                });

                btn.addEventListener('dragend', () => {
                    btn.classList.remove('doc-card-dragging');
                    if (currentDropCol) {
                        currentDropCol.classList.remove('saturday-col-drop-active');
                        currentDropCol = null;
                    }
                    colMarkers.forEach(c => {
                        c.classList.remove('saturday-col-droppable-hint', 'saturday-col-drop-active', 'saturday-col-blocked-sequence');
                    });
                    setTimeout(() => {
                        isDraggingCard = false;
                        btn.dataset.isDragging = "false";
                    }, 150);
                });

                btn.addEventListener('click', (e) => {
                    if (isDraggingCard || btn.dataset.isDragging === "true") {
                        e.preventDefault();
                        e.stopImmediatePropagation();
                        return false;
                    }
                }, true);
            });

            // 2. Configurar columna como zona de soltado (Drop Target optimizado sin sobrecarga)
            if (!col.dataset.dropTargetBound) {
                col.dataset.dropTargetBound = "true";

                col.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    if (col.classList.contains('saturday-col-blocked-sequence')) {
                        e.dataTransfer.dropEffect = 'none';
                        return;
                    }
                    e.dataTransfer.dropEffect = 'move';
                    if (currentDropCol !== col) {
                        if (currentDropCol) currentDropCol.classList.remove('saturday-col-drop-active');
                        currentDropCol = col;
                        col.classList.add('saturday-col-drop-active');
                    }
                });

                col.addEventListener('dragleave', (e) => {
                    if (!col.contains(e.relatedTarget)) {
                        col.classList.remove('saturday-col-drop-active');
                        if (currentDropCol === col) currentDropCol = null;
                    }
                });

                col.addEventListener('drop', (e) => {
                    e.preventDefault();
                    if (currentDropCol) {
                        currentDropCol.classList.remove('saturday-col-drop-active');
                        currentDropCol = null;
                    }
                    colMarkers.forEach(c => c.classList.remove('saturday-col-droppable-hint', 'saturday-col-blocked-sequence'));

                    const jsonStr = e.dataTransfer.getData('text/plain');
                    if (!jsonStr) return;

                    try {
                        const data = JSON.parse(jsonStr);
                        const marker = col.querySelector('.saturday-col-marker');
                        const targetDate = marker ? marker.getAttribute('data-sat-date') : null;

                        if (!targetDate || data.source_date === targetDate) {
                            return;
                        }

                        // Validación de secuencia estricta: Bloquear si es la misma secuencia
                        if (sonMismaSecuencia(data.source_date, targetDate)) {
                            const mostrarAlertaSecuencia = () => {
                                if (window.parent && window.parent.Swal) {
                                    window.parent.Swal.fire({
                                        title: "Secuencia no permitida",
                                        text: "No puedes mover a este médico a su misma secuencia. Debe trasladarse a su secuencia contraria (ej. 21 de noviembre o 5 de diciembre).",
                                        icon: "warning",
                                        confirmButtonColor: '#0f9a9b'
                                    });
                                } else {
                                    alert("Secuencia no permitida: No puedes mover a este médico a su misma secuencia. Debe ser a la secuencia contraria.");
                                }
                            };

                            if (!window.parent.Swal) {
                                const sc = window.parent.document.createElement('script');
                                sc.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                                sc.onload = mostrarAlertaSecuencia;
                                window.parent.document.head.appendChild(sc);
                            } else {
                                mostrarAlertaSecuencia();
                            }
                            return;
                        }

                        data.target_date = targetDate;

                        // Notificación visual inmediata
                        mostrarIndicadorCargaPanel();

                        let targetInput = parentDoc.querySelector('div[class*="st-key-bridge_drag_drop_payload"] input, input[aria-label="dd_bridge_input"]');
                        if (!targetInput) {
                            const allInputs = parentDoc.querySelectorAll('input');
                            for (let inp of allInputs) {
                                if (inp.getAttribute('aria-label') === 'dd_bridge_input') {
                                    targetInput = inp;
                                    break;
                                }
                            }
                        }

                        let targetBtn = parentDoc.querySelector('div[class*="st-key-btn_trigger_drag_drop"] button, button[data-testid*="btn_trigger_drag_drop"]');
                        if (!targetBtn) {
                            const allBtns = parentDoc.querySelectorAll('button');
                            for (let b of allBtns) {
                                const txt = (b.innerText || "").trim();
                                if (txt === 'dd_bridge_btn') {
                                    targetBtn = b;
                                    break;
                                }
                            }
                        }

                        // Asignar el payload al input puente y comprometer el valor en el estado de Streamlit
                        if (targetInput) {
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeInputValueSetter.call(targetInput, JSON.stringify(data));
                            targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                            targetInput.dispatchEvent(new Event('change', { bubbles: true }));

                            // Disparar Enter para que el componente React de Streamlit registre y transmita el valor
                            targetInput.focus();
                            targetInput.dispatchEvent(new KeyboardEvent('keydown', {
                                bubbles: true,
                                cancelable: true,
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13
                            }));
                            targetInput.blur();
                        }

                        // Respaldo de activación para garantizar la apertura inmediata del panel
                        if (targetBtn) {
                            setTimeout(() => {
                                targetBtn.click();
                            }, 50);
                        }
                    } catch (err) {
                        console.error("Error al procesar drop:", err);
                    }
                });
            }
        });
    }

    // Inicialización rápida y sincronización de eventos
    vincularBuscadorReactivo();
    inicializarDragAndDrop();
    vincularFiltrosExcel();
    const timers = [100, 300, 1000];
    timers.forEach(ms => {
        setTimeout(() => {
            vincularBuscadorReactivo();
            inicializarDragAndDrop();
            vincularFiltrosExcel();
        }, ms);
    });

    // Vincular activamente al interactuar con popovers de fecha/filtro
    parentDoc.addEventListener('click', (e) => {
        if (e.target && e.target.closest && (
            e.target.closest('[class*="st-key-popover_filtro"]') || 
            e.target.closest('[data-testid="stPopover"]') || 
            e.target.closest('.custom-header-btn')
        )) {
            setTimeout(vincularFiltrosExcel, 30);
            setTimeout(vincularFiltrosExcel, 120);
            setTimeout(vincularFiltrosExcel, 300);
        }
    }, true);

    // MutationObserver para registrar popovers dinámicos al abrirse
    if (!window._popoverFilterObserver) {
        window._popoverFilterObserver = new MutationObserver((mutations) => {
            let foundPopover = false;
            for (let m of mutations) {
                for (let n of m.addedNodes) {
                    if (n.nodeType === 1 && (
                        (n.matches && (n.matches('[data-testid="stPopoverBody"]') || n.matches('[data-testid="stCheckbox"]'))) || 
                        (n.querySelector && (n.querySelector('[data-testid="stPopoverBody"]') || n.querySelector('[data-testid="stCheckbox"]')))
                    )) {
                        foundPopover = true;
                        break;
                    }
                }
                if (foundPopover) break;
            }
            if (foundPopover) {
                vincularFiltrosExcel();
                setTimeout(vincularFiltrosExcel, 40);
                setTimeout(vincularFiltrosExcel, 120);
            }
        });
        window._popoverFilterObserver.observe(parentDoc.body, { childList: true, subtree: true });
    }
    </script>
    """, height=0)

    # Alerta de error si no se encuentra el nombre buscado tras presionar Enter
    if st.session_state.get("show_error_alert", False):
        alert_id = datetime.datetime.now().timestamp()
        st.components.v1.html(f"""
        <script>
            try {{
                const runAlert = () => {{
                    window.parent.Swal.fire({{
                        title: "Error",
                        text: "El nombre no existe, ingrese un nuevo nombre",
                        icon: "error",
                        draggable: true,
                        confirmButtonColor: '#1a73e8'
                    }});
                }};

                if (!window.parent.Swal) {{
                    const script = window.parent.document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
                    script.onload = runAlert;
                    window.parent.document.head.appendChild(script);
                }} else {{
                    runAlert();
                }}
            }} catch (e) {{
                console.error("SweetAlert2 parent injection failed:", e);
            }}
        </script>
        """, height=0)
        st.session_state["show_error_alert"] = False

    return search_query, st.session_state["filter_class"]
