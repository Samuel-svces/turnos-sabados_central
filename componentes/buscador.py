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
                const cardContainer = metaContainer ? metaContainer.nextElementSibling : null;
                const btn = cardContainer ? cardContainer.querySelector('button') : null;
                if (!cardContainer || !btn) return;

                if (!cleanTerm) {
                    cardContainer.classList.remove('search-card-hidden');
                    cardContainer.style.removeProperty('display');
                    btn.classList.remove('search-highlight-active', 'search-dimmed');
                    return;
                }

                if (docName.includes(cleanTerm)) {
                    cardContainer.classList.remove('search-card-hidden');
                    cardContainer.style.removeProperty('display');
                    btn.classList.remove('search-dimmed');
                    btn.classList.add('search-highlight-active');
                } else {
                    cardContainer.classList.add('search-card-hidden');
                    cardContainer.style.setProperty('display', 'none', 'important');
                    btn.classList.remove('search-highlight-active');
                    btn.classList.add('search-dimmed');
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
                const badge = wrap.querySelector('.doc-name-badge') || wrap;
                const rawText = (badge.innerText || badge.textContent || "").trim();
                const docText = normalizarTexto(rawText);
                const cont = wrap.closest('div[data-testid="stElementContainer"]') || wrap;

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

    function sincronizarBusquedaConStreamlit(val) {
        const parentDoc = window.parent.document;
        const clean = (val || "").trim();
        if (clean === lastSyncedVal) return;
        lastSyncedVal = clean;

        let inputEl = parentDoc.querySelector('input[aria-label="Buscador"], div[data-testid="stTextInput"] input');
        if (!inputEl) return;

        // Disparar Enter de manera limpia para sincronizar el estado global en Streamlit
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeSetter.call(inputEl, clean);
        inputEl.dispatchEvent(new Event('input', { bubbles: true }));
        inputEl.dispatchEvent(new Event('change', { bubbles: true }));
        inputEl.dispatchEvent(new KeyboardEvent('keydown', {
            bubbles: true,
            cancelable: true,
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13
        }));
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
                const val = e.target.value;
                if (rafSearchId) cancelAnimationFrame(rafSearchId);
                rafSearchId = requestAnimationFrame(() => {
                    aplicarBusquedaEnVivo(val);
                });

                // 2. Búsqueda automática entre columnas sin requerir presionar Enter obligatoriamente
                if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
                searchDebounceTimer = setTimeout(() => {
                    sincronizarBusquedaConStreamlit(val);
                }, 400);
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
        const popoverSearchInputs = parentDoc.querySelectorAll('[data-testid="stPopoverBody"] input[placeholder="Buscar..."]');
        popoverSearchInputs.forEach(input => {
            if (input.dataset.excelFilterBound) return;
            input.dataset.excelFilterBound = "true";
            input.addEventListener('input', (e) => {
                const query = normalizarTexto(e.target.value);
                const popover = input.closest('[data-testid="stPopoverBody"]');
                if (!popover) return;
                const labels = popover.querySelectorAll('label[data-testid="stCheckbox"]');
                labels.forEach((lbl, idx) => {
                    if (idx === 0 && lbl.textContent.includes("Seleccionar")) return;
                    const txt = normalizarTexto(lbl.textContent);
                    const cont = lbl.closest('div[data-testid="stElementContainer"]') || lbl;
                    if (!query || txt.includes(query)) {
                        cont.style.removeProperty('display');
                    } else {
                        cont.style.setProperty('display', 'none', 'important');
                    }
                });
            });
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
    const timers = [60, 200, 500, 1000];
    timers.forEach(ms => {
        setTimeout(() => {
            vincularBuscadorReactivo();
            inicializarDragAndDrop();
            vincularFiltrosExcel();
        }, ms);
    });
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
