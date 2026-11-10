"""
buscador.py
-----------
Componente de búsqueda reactiva en vivo y filtros de clasificación de turnos.
Centra el input de búsqueda en pantalla, elimina los botones manuales y aplica
un subrayado y resaltado dinámico en tiempo real letra por letra sin requerir Enter.
"""

import streamlit as st
import datetime


def renderizar_buscador():
    """
    Renderiza el buscador reactivo centrado y los filtros dinámicos por clasificación.
    Retorna:
        search_query (str): Término de búsqueda en mayúsculas (si se completó con Enter o estado previo).
        filtro_clasificacion (str): Filtro activo ('Todos', 'Secuencia Normal', 'Compensación').
    """
    if "input_busqueda_medico" not in st.session_state:
        st.session_state["input_busqueda_medico"] = ""

    if st.session_state.get("clear_search_flag", False):
        st.session_state["input_busqueda_medico"] = ""
        st.session_state["clear_search_flag"] = False

    # Fila de Buscador Centrado en Pantalla (sin botones manuales B, L, R)
    col_spacer_l, col_search_center, col_spacer_r = st.columns([1.5, 3.0, 1.5])
    with col_search_center:
        st.markdown("<div class='custom-search-marker'></div>", unsafe_allow_html=True)
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
        if (el.closest('[data-testid="stPopover"]')) return true;
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
            // MODO ADMINISTRADOR: Botones de turno
            const adminButtons = col.querySelectorAll('button');
            adminButtons.forEach(btn => {
                if (esControlFiltro(btn)) return;
                const rawText = (btn.innerText || btn.textContent || "").trim();
                if (!rawText) return;

                // Encabezados de fecha: SIEMPRE visibles
                if (/^\d/.test(rawText) || btn.classList.contains('custom-header-btn')) {
                    return;
                }

                // Botones de acción (Agregar Médico, Duplicar): ocultar durante búsqueda activa
                if (rawText.includes("Agregar Médico") || rawText.includes("Duplicar") || rawText.includes("⚙️")) {
                    const cont = btn.closest('div[data-testid="stElementContainer"]') || btn.parentElement;
                    if (cont) {
                        if (cleanTerm) {
                            cont.style.setProperty('display', 'none', 'important');
                        } else {
                            cont.style.removeProperty('display');
                        }
                    }
                    return;
                }

                // Botón de médico individual
                const cont = btn.closest('div[data-testid="stElementContainer"]') || btn;
                const docText = normalizarTexto(rawText);

                if (!cleanTerm) {
                    // Sin búsqueda: restaurar todo visible y limpio
                    if (cont) cont.style.removeProperty('display');
                    btn.style.removeProperty('display');
                    btn.classList.remove('search-highlight-active', 'search-dimmed');
                    return;
                }

                if (docText.includes(cleanTerm)) {
                    // Coincide: mostrar inmediatamente y resaltar para que se vea apenas se escribe
                    if (cont) cont.style.removeProperty('display');
                    btn.style.removeProperty('display');
                    btn.classList.remove('search-dimmed');
                    btn.classList.add('search-highlight-active');
                } else {
                    // No coincide: ocultar por completo para que los que coinciden suban y se vean al instante
                    if (cont) {
                        cont.style.setProperty('display', 'none', 'important');
                    } else {
                        btn.style.setProperty('display', 'none', 'important');
                    }
                    btn.classList.remove('search-highlight-active');
                    btn.classList.add('search-dimmed');
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
                    if (cont) cont.style.removeProperty('display');
                    wrap.style.removeProperty('display');
                    badge.classList.remove('search-highlight-active', 'search-dimmed');
                    return;
                }

                if (docText.includes(cleanTerm)) {
                    // Coincide: mostrar inmediatamente
                    if (cont) cont.style.removeProperty('display');
                    wrap.style.removeProperty('display');
                    badge.classList.remove('search-dimmed');
                    badge.classList.add('search-highlight-active');
                } else {
                    // No coincide: ocultar
                    if (cont) {
                        cont.style.setProperty('display', 'none', 'important');
                    } else {
                        wrap.style.setProperty('display', 'none', 'important');
                    }
                    badge.classList.remove('search-highlight-active');
                    badge.classList.add('search-dimmed');
                }
            });
        });
    }

    const aplicarBusquedaEnVivo = aplicarResaltadoEnVivo;

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

        // Limpiar placeholder y evitar cualquier autofill o tooltip emergente nativo
        inputBuscador.placeholder = "";
        inputBuscador.setAttribute("placeholder", "");
        inputBuscador.setAttribute("autocomplete", "off");
        inputBuscador.setAttribute("autocorrect", "off");
        inputBuscador.setAttribute("autocapitalize", "off");
        inputBuscador.setAttribute("spellcheck", "false");
        inputBuscador.setAttribute("name", "filtro_vivo_medicos");

        // Ocultar cualquier tooltip de instrucciones de Streamlit adyacente
        const containerInput = inputBuscador.closest('div[data-testid="stTextInput"]');
        if (containerInput) {
            const tooltips = containerInput.querySelectorAll('[data-testid="stTextInputInstructions"], [data-testid="InputInstructions"], .stTextInputInstructions');
            tooltips.forEach(t => t.style.setProperty('display', 'none', 'important'));
        }

        if (!inputBuscador.dataset.liveSearchBound) {
            inputBuscador.dataset.liveSearchBound = "true";
            
            // Filtrado reactivo inmediato con cada letra pulsada
            inputBuscador.addEventListener('input', (e) => {
                aplicarBusquedaEnVivo(e.target.value);
            });

            inputBuscador.addEventListener('focus', () => {
                if (inputBuscador.value) aplicarBusquedaEnVivo(inputBuscador.value);
            });

            inputBuscador.addEventListener('paste', () => {
                setTimeout(() => aplicarBusquedaEnVivo(inputBuscador.value), 20);
            });

            // Tecla Escape para restablecer instantáneamente
            inputBuscador.addEventListener('keydown', (e) => {
                if (e.key === "Escape") {
                    inputBuscador.value = "";
                    aplicarBusquedaEnVivo("");
                }
            });
        }

        // Si ya hay un valor cargado, aplicar el filtrado de inmediato
        if (inputBuscador.value) {
            aplicarBusquedaEnVivo(inputBuscador.value);
        }
        return true;
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

                btn.addEventListener('dragstart', (e) => {
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
                            targetCol.classList.add('saturday-col-droppable-hint');
                        }
                    });
                });

                btn.addEventListener('dragend', () => {
                    btn.classList.remove('doc-card-dragging');
                    colMarkers.forEach(c => {
                        c.classList.remove('saturday-col-droppable-hint', 'saturday-col-drop-active');
                    });
                });
            });

            // 2. Configurar columna como zona de soltado (Drop Target)
            if (!col.dataset.dropTargetBound) {
                col.dataset.dropTargetBound = "true";

                col.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                    if (!col.classList.contains('saturday-col-drop-active')) {
                        col.classList.add('saturday-col-drop-active');
                    }
                });

                col.addEventListener('dragleave', (e) => {
                    if (!col.contains(e.relatedTarget)) {
                        col.classList.remove('saturday-col-drop-active');
                    }
                });

                col.addEventListener('drop', (e) => {
                    e.preventDefault();
                    col.classList.remove('saturday-col-drop-active');
                    colMarkers.forEach(c => c.classList.remove('saturday-col-droppable-hint'));

                    const jsonStr = e.dataTransfer.getData('text/plain');
                    if (!jsonStr) return;

                    try {
                        const data = JSON.parse(jsonStr);
                        const marker = col.querySelector('.saturday-col-marker');
                        const targetDate = marker ? marker.getAttribute('data-sat-date') : null;

                        if (!targetDate || data.source_date === targetDate) {
                            return;
                        }

                        data.target_date = targetDate;

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

                        // Ocultar preventivamente los contenedores
                        if (targetInput) {
                            const cont = targetInput.closest('div[data-testid="stElementContainer"]') || targetInput.parentElement;
                            if (cont) cont.style.setProperty('display', 'none', 'important');
                        }
                        if (targetBtn) {
                            const cont = targetBtn.closest('div[data-testid="stElementContainer"]') || targetBtn.parentElement;
                            if (cont) cont.style.setProperty('display', 'none', 'important');
                        }

                        if (targetInput) {
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeInputValueSetter.call(targetInput, JSON.stringify(data));
                            targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                            targetInput.dispatchEvent(new Event('change', { bubbles: true }));

                            // Disparar Enter para que Streamlit capture el evento directamente
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

                        if (targetBtn) {
                            setTimeout(() => targetBtn.click(), 40);
                        }
                    } catch (err) {
                        console.error("Error al procesar drop:", err);
                    }
                });
            }
        });
    }

    // Inicialización rápida y reintentos ligeros
    vincularBuscadorReactivo();
    inicializarDragAndDrop();
    const timers = [50, 150, 300, 600, 1200];
    timers.forEach(ms => {
        setTimeout(() => {
            vincularBuscadorReactivo();
            inicializarDragAndDrop();
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
