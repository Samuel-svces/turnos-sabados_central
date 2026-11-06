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

    # Inicializar estado para el filtro de clasificación si no existe
    if "filter_class" not in st.session_state:
        st.session_state["filter_class"] = "Todos"

    if not st.session_state.is_admin:
        # Fila de píldoras/botones de filtro dinámico compactos y juntos
        col_lbl_f, col_btn_f1, col_btn_f2, col_btn_f3 = st.columns([1, 1, 1, 1])
        with col_lbl_f:
            st.markdown("<div class='filter-row-marker filter-label-wrap'>Filtrar por:</div>", unsafe_allow_html=True)
        with col_btn_f1:
            st.markdown("<div class='filter-all-marker'></div>", unsafe_allow_html=True)
            f_style_all = "primary" if st.session_state["filter_class"] == "Todos" else "secondary"
            if st.button("Todos", key="btn_filtro_todos", use_container_width=False, type=f_style_all):
                st.session_state["filter_class"] = "Todos"
                st.rerun()
        with col_btn_f2:
            st.markdown("<div class='filter-normal-marker'></div>", unsafe_allow_html=True)
            f_style_normal = "primary" if st.session_state["filter_class"] == "Secuencia Normal" else "secondary"
            if st.button("Normal", key="btn_filtro_secuencia_normal", use_container_width=False, type=f_style_normal):
                st.session_state["filter_class"] = "Secuencia Normal"
                st.rerun()
        with col_btn_f3:
            st.markdown("<div class='filter-comp-marker'></div>", unsafe_allow_html=True)
            f_style_comp = "primary" if st.session_state["filter_class"] == "Compensación" else "secondary"
            if st.button("Compensación", key="btn_filtro_compensacion", use_container_width=False, type=f_style_comp):
                st.session_state["filter_class"] = "Compensación"
                st.rerun()
    else:
        st.session_state["filter_class"] = "Todos"

    # Inyección de script reactivo en tiempo real para estilizar y subrayar con cada pulsación de tecla
    st.components.v1.html(r"""
    <script>
    function normalizarTexto(txt) {
        return (txt || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim()
            .toUpperCase();
    }

    function aplicarResaltadoEnVivo(termino) {
        const parentDoc = window.parent.document;
        const cleanTerm = normalizarTexto(termino);
        
        // Elementos de médico en modo administrador (botones) y modo público (badges)
        const items = parentDoc.querySelectorAll('div[data-testid="stColumn"]:has(.saturday-col-marker) button, .doc-name-badge');

        items.forEach(item => {
            const rawText = (item.innerText || item.textContent || "").trim();
            // Omitir botones que son encabezados con fecha, agregar médico, o el popover admin
            if (!rawText || /^\d/.test(rawText) || rawText.includes("Agregar Médico") || rawText.includes("⚙️")) {
                return;
            }

            if (!cleanTerm) {
                // Sin término de búsqueda: restablecer estilos
                item.classList.remove('search-highlight-active', 'search-dimmed');
                item.style.removeProperty('text-decoration');
                item.style.removeProperty('text-decoration-color');
                item.style.removeProperty('text-decoration-thickness');
                item.style.removeProperty('text-underline-offset');
                item.style.removeProperty('background-color');
                item.style.removeProperty('box-shadow');
                item.style.removeProperty('opacity');

                item.querySelectorAll('p, span, div').forEach(c => {
                    c.style.removeProperty('text-decoration');
                    c.style.removeProperty('text-decoration-color');
                    c.style.removeProperty('text-decoration-thickness');
                    c.style.removeProperty('text-underline-offset');
                });
                return;
            }

            const itemText = normalizarTexto(rawText);
            if (itemText.includes(cleanTerm)) {
                // Coincidencia: resaltar con subrayado visible
                item.classList.remove('search-dimmed');
                item.classList.add('search-highlight-active');
                item.style.setProperty('text-decoration', 'underline', 'important');
                item.style.setProperty('text-decoration-color', '#0f9a9b', 'important');
                item.style.setProperty('text-decoration-thickness', '3px', 'important');
                item.style.setProperty('text-underline-offset', '4px', 'important');
                item.style.setProperty('background-color', '#ecfdf5', 'important');
                item.style.setProperty('box-shadow', '0 0 10px rgba(15, 154, 155, 0.35)', 'important');
                item.style.setProperty('opacity', '1', 'important');

                item.querySelectorAll('p, span, div').forEach(c => {
                    c.style.setProperty('text-decoration', 'underline', 'important');
                    c.style.setProperty('text-decoration-color', '#0f9a9b', 'important');
                    c.style.setProperty('text-decoration-thickness', '3px', 'important');
                    c.style.setProperty('text-underline-offset', '4px', 'important');
                });
            } else {
                // No coincide: atenuar sutilmente
                item.classList.remove('search-highlight-active');
                item.classList.add('search-dimmed');
                item.style.removeProperty('text-decoration');
                item.style.removeProperty('text-decoration-color');
                item.style.removeProperty('text-decoration-thickness');
                item.style.removeProperty('text-underline-offset');
                item.style.removeProperty('background-color');
                item.style.removeProperty('box-shadow');
                item.style.setProperty('opacity', '0.28', 'important');

                item.querySelectorAll('p, span, div').forEach(c => {
                    c.style.removeProperty('text-decoration');
                    c.style.removeProperty('text-decoration-color');
                    c.style.removeProperty('text-decoration-thickness');
                    c.style.removeProperty('text-underline-offset');
                });
            }
        });
    }

    function vincularBuscadorReactivo() {
        const parentDoc = window.parent.document;
        // Localizar el input del buscador de forma resiliente
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
        if (!inputBuscador) return;

        // Asegurar que el placeholder esté completamente vacío
        inputBuscador.placeholder = "";
        inputBuscador.setAttribute("placeholder", "");

        // Asegurar borde verde agua suave, fondo blanco y esquinas redondeadas
        const baseInput = inputBuscador.closest('div[data-baseweb="input"], [data-baseweb="base-input"]') || inputBuscador.parentElement;
        if (baseInput) {
            baseInput.style.setProperty('background-color', '#ffffff', 'important');
            baseInput.style.setProperty('background', '#ffffff', 'important');
            baseInput.style.setProperty('border', '1.5px solid #5ec2ba', 'important');
            baseInput.style.setProperty('border-radius', '14px', 'important');
            baseInput.style.setProperty('box-shadow', 'none', 'important');
            baseInput.style.setProperty('box-sizing', 'border-box', 'important');
            baseInput.style.setProperty('max-width', '340px', 'important');
            baseInput.style.setProperty('margin', '0 auto', 'important');
        }

        inputBuscador.style.setProperty('background-image', 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%230f9a9b\' stroke-width=\'2.2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><circle cx=\'11\' cy=\'11\' r=\'7\'></circle><line x1=\'21\' y1=\'21\' x2=\'16\' y2=\'16\'></line></svg>")', 'important');
        inputBuscador.style.setProperty('background-repeat', 'no-repeat', 'important');
        inputBuscador.style.setProperty('background-position', '11px center', 'important');
        inputBuscador.style.setProperty('background-size', '16px 16px', 'important');
        inputBuscador.style.setProperty('padding-left', '36px', 'important');
        inputBuscador.style.setProperty('border', 'none', 'important');
        inputBuscador.style.setProperty('outline', 'none', 'important');
        inputBuscador.style.setProperty('border-radius', '14px', 'important');

        if (!inputBuscador.dataset.liveSearchBound) {
            inputBuscador.dataset.liveSearchBound = "true";
            
            // Escuchar cada letra escrita en tiempo real
            inputBuscador.addEventListener('input', (e) => {
                aplicarResaltadoEnVivo(e.target.value);
            });

            // Restablecer al presionar Escape
            inputBuscador.addEventListener('keydown', (e) => {
                if (e.key === "Escape") {
                    inputBuscador.value = "";
                    aplicarResaltadoEnVivo("");
                }
            });
        }

        // Si ya hay un valor cargado, aplicar resaltado inmediatamente
        if (inputBuscador.value) {
            aplicarResaltadoEnVivo(inputBuscador.value);
        }
    }

    function alinearFiltrosCentrados() {
        const parentDoc = window.parent.document;
        // Localizar el marcador dentro de la fila de filtros
        const filterMarker = parentDoc.querySelector('.filter-all-marker, .filter-row-marker, .filter-normal-marker, .filter-comp-marker');
        if (!filterMarker) return;

        const filterRow = filterMarker.closest('[data-testid="stHorizontalBlock"], [data-testid="horizontalBlock"]');
        if (!filterRow) return;

        filterRow.style.setProperty('display', 'flex', 'important');
        filterRow.style.setProperty('flex-direction', 'row', 'important');
        filterRow.style.setProperty('justify-content', 'center', 'important');
        filterRow.style.setProperty('align-items', 'center', 'important');
        filterRow.style.setProperty('gap', '0.45rem', 'important');
        filterRow.style.setProperty('margin', '0.15rem auto', 'important');
        filterRow.style.setProperty('width', '100%', 'important');

        const cols = filterRow.querySelectorAll(':scope > [data-testid="stColumn"], :scope > [data-testid="column"]');
        cols.forEach(c => {
            c.style.setProperty('flex', '0 0 auto', 'important');
            c.style.setProperty('width', 'auto', 'important');
            c.style.setProperty('min-width', 'unset', 'important');
            c.style.setProperty('max-width', 'unset', 'important');
            c.style.setProperty('padding', '0', 'important');
            c.style.setProperty('margin', '0', 'important');

            c.querySelectorAll('[data-testid="stElementContainer"], .stButton').forEach(el => {
                el.style.setProperty('width', 'auto', 'important');
                el.style.setProperty('min-width', 'unset', 'important');
                el.style.setProperty('margin', '0', 'important');
            });

            c.querySelectorAll('button').forEach(btn => {
                btn.style.setProperty('width', 'auto', 'important');
                btn.style.setProperty('min-width', 'unset', 'important');
                btn.style.setProperty('margin', '0', 'important');
            });
        });
    }

    function styleButtons() {
        const parentDoc = window.parent.document;
        const colButtons = parentDoc.querySelectorAll('div[data-testid="stColumn"]:has(.saturday-col-marker) button');
        colButtons.forEach(btn => {
            const text = (btn.innerText || "").trim();
            if (!text) return;
            if (text.includes('⚙️')) return;
            
            // Encabezado de fecha
            if (/^\d/.test(text)) {
                btn.classList.add('custom-header-btn');
                btn.style.setProperty('background', 'linear-gradient(180deg, #1b8dfd 0%, #0866ea 100%)', 'important');
                btn.style.setProperty('background-color', '#0866ea', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.style.setProperty('border', 'none', 'important');
                btn.style.setProperty('border-radius', '8px', 'important');
                btn.style.setProperty('box-shadow', '0 3px 10px rgba(8, 102, 234, 0.3)', 'important');
                btn.style.setProperty('font-weight', '700', 'important');
                btn.style.setProperty('font-size', '0.88rem', 'important');
                btn.style.setProperty('letter-spacing', '0.2px', 'important');
                btn.style.setProperty('padding', '0.35rem 0.5rem', 'important');
                btn.style.setProperty('margin-bottom', '0.35rem', 'important');
                btn.style.setProperty('text-shadow', '0 1px 2px rgba(0, 0, 0, 0.15)', 'important');
                const pHeader = btn.querySelector('p, span');
                if (pHeader) {
                    pHeader.style.setProperty('color', '#ffffff', 'important');
                    pHeader.style.setProperty('font-weight', '700', 'important');
                }
                return;
            }

            // Botón Agregar Médico
            if (text.includes("Agregar Médico")) {
                btn.style.setProperty('background-color', 'rgb(20, 116, 220)', 'important');
                btn.style.setProperty('background', 'rgb(20, 116, 220)', 'important');
                btn.style.setProperty('border-color', 'rgb(20, 116, 220)', 'important');
                btn.style.setProperty('color', '#ffffff', 'important');
                btn.querySelectorAll('*').forEach(el => el.style.setProperty('color', '#ffffff', 'important'));
                return;
            }

            // Ignorar Duplicar
            if (text.includes("Duplicar")) {
                return;
            }

            let bg = '#ffffff';
            let fg = '#262730';
            let border = 'rgba(49, 51, 63, 0.2)';
            let shadow = '0 1px 2px rgba(0, 0, 0, 0.04)';

            if (text.includes('🎯')) {
                bg = '#fff8e1';
                fg = '#e65100';
                border = '#ffc107';
                shadow = '0 0 12px rgba(255, 193, 7, 0.4)';
            } else if (text.includes('DUPLICADO') || text.includes('🚨')) {
                bg = '#ffebee';
                fg = '#c62828';
                border = '#ffcdd2';
            } else if (text.includes('COMP') || text.includes('🟡')) {
                bg = '#fffde6';
                fg = '#b58900';
                border = '#ffecb3';
            } else if (text.includes('Cambio') || text.includes('🔄')) {
                bg = '#e8f5e9';
                fg = '#2e7d32';
                border = '#c8e6c9';
            }

            // Si no está resaltado por la búsqueda activa en vivo, aplicar estilos base
            if (!btn.classList.contains('search-highlight-active')) {
                btn.style.setProperty('background', bg, 'important');
                btn.style.setProperty('background-color', bg, 'important');
                btn.style.setProperty('color', fg, 'important');
                btn.style.setProperty('border-color', border, 'important');
                btn.style.setProperty('box-shadow', shadow, 'important');
            }

            btn.style.setProperty('border-style', 'solid', 'important');
            btn.style.setProperty('border-width', '1px', 'important');
            btn.style.setProperty('border-radius', '8px', 'important');
            btn.style.setProperty('font-weight', '500', 'important');
            btn.style.setProperty('font-size', '0.8rem', 'important');
            btn.style.setProperty('padding', '0.22rem 0.5rem', 'important');
            btn.style.setProperty('width', '100%', 'important');
            btn.style.setProperty('display', 'block', 'important');
            btn.style.setProperty('margin-bottom', '0px', 'important');
            btn.style.setProperty('min-height', 'auto', 'important');
            btn.style.setProperty('line-height', '1.15', 'important');
            btn.style.setProperty('text-shadow', 'none', 'important');

            const childs = btn.querySelectorAll('*');
            childs.forEach(c => {
                if (!btn.classList.contains('search-highlight-active')) {
                    c.style.setProperty('color', fg, 'important');
                }
                c.style.setProperty('background-color', 'transparent', 'important');
                c.style.setProperty('text-shadow', 'none', 'important');
            });
        });

        // Asegurar que el input del buscador reactivo y los filtros estén vinculados
        vincularBuscadorReactivo();
        alinearFiltrosCentrados();
    }

    styleButtons();
    vincularBuscadorReactivo();
    alinearFiltrosCentrados();
    const observer = new MutationObserver(() => {
        styleButtons();
        vincularBuscadorReactivo();
        alinearFiltrosCentrados();
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
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
