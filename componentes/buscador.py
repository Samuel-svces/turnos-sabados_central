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
            placeholder="Buscar médico...", 
            label_visibility="collapsed"
        ).strip().upper()

    # Inicializar estado para el filtro de clasificación si no existe
    if "filter_class" not in st.session_state:
        st.session_state["filter_class"] = "Todos"

    if not st.session_state.is_admin:
        # Fila de píldoras/botones de filtro dinámico
        st.markdown("<div style='margin-top: 0.15rem;'></div>", unsafe_allow_html=True)
        col_spacer_l, col_lbl_f, col_btn_f1, col_btn_f2, col_btn_f3, col_spacer_r = st.columns([2.2, 1.2, 1.8, 1.8, 2.2, 2.2])
        with col_lbl_f:
            st.markdown("<div style='font-size: 0.95rem; color: #555; font-weight: bold; padding-top: 0.35rem; text-align: right; font-family: Outfit;'>Filtrar por:</div>", unsafe_allow_html=True)
        with col_btn_f1:
            st.markdown("<div class='filter-all-marker'></div>", unsafe_allow_html=True)
            f_style_all = "primary" if st.session_state["filter_class"] == "Todos" else "secondary"
            if st.button("Todos", key="btn_filtro_todos", use_container_width=True, type=f_style_all):
                st.session_state["filter_class"] = "Todos"
                st.rerun()
        with col_btn_f2:
            st.markdown("<div class='filter-normal-marker'></div>", unsafe_allow_html=True)
            f_style_normal = "primary" if st.session_state["filter_class"] == "Secuencia Normal" else "secondary"
            if st.button("Normal", key="btn_filtro_secuencia_normal", use_container_width=True, type=f_style_normal):
                st.session_state["filter_class"] = "Secuencia Normal"
                st.rerun()
        with col_btn_f3:
            st.markdown("<div class='filter-comp-marker'></div>", unsafe_allow_html=True)
            f_style_comp = "primary" if st.session_state["filter_class"] == "Compensación" else "secondary"
            if st.button("Compensación", key="btn_filtro_compensacion", use_container_width=True, type=f_style_comp):
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

        // Asegurar que el input del buscador reactivo esté vinculado
        vincularBuscadorReactivo();
    }

    styleButtons();
    vincularBuscadorReactivo();
    const observer = new MutationObserver(() => {
        styleButtons();
        vincularBuscadorReactivo();
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
