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

    // Inicialización rápida y reintentos ligeros
    if (!vincularBuscadorReactivo()) {
        const timers = [50, 150, 300, 600];
        timers.forEach(ms => setTimeout(vincularBuscadorReactivo, ms));
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
