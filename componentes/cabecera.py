"""
cabecera.py
-----------
Componente de interfaz para la cabecera institucional, identidad de marca,
perfil de usuario y popover de administración con sincronización y purga de SharePoint.
"""

import streamlit as st
import datetime
import os
import json
from modulos import procesador_datos as dp
from modulos import cliente_sharepoint as gc


def renderizar_cabecera(logo_b64: str, cargar_datos_fn):
    """
    Renderiza el Topbar de esquina a esquina con el logo institucional,
    el título 'Conexión operativa' y el botón de usuario con popover de administración.
    """
    col_top_brand, col_top_user = st.columns([1, 1])

    with col_top_brand:
        img_src = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
        st.markdown(f"""
            <div class="topbar-brand" style="display:flex; align-items:center; gap:0.5rem; user-select:none;">
                <img src="{img_src}" class="topbar-logo" style="height:28px; max-height:30px; width:auto; object-fit:contain; display:block;" alt="Unión para la Salud y la Vida S.A.S.">
                <span class="topbar-brand-divider" style="display:inline-block; width:1px; height:22px; background-color:#cbd5e1; margin:0 0.85rem;"></span>
                <div class="topbar-titles"><span class="topbar-title" style="font-family:'Outfit', sans-serif; font-size:1.15rem; font-weight:700; color:#0f172a; white-space:nowrap; letter-spacing:-0.2px;">Conexión operativa</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col_top_user:
        st.markdown("<div class='topbar-user-marker'></div>", unsafe_allow_html=True)
        with st.popover("Conexión Operativa"):
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.5rem;">
                    <div style="width: 34px; height: 34px; border-radius: 50%; background-color: #e7f6f4; color: #0d9488; display: flex; align-items: center; justify-content: center; font-size: 1.15rem;">
                        <i class="bi bi-person"></i>
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 0.95rem; color: #0f172a; line-height: 1.2;">Administrador</div>
                    </div>
                </div>
                <div style="margin: 0.5rem 0 0.8rem 0; border-top: 1px solid #e2e8f0;"></div>
            """, unsafe_allow_html=True)

            if st.session_state.is_admin:
                st.success("Sesión Iniciada (Admin)", icon=":material/verified_user:")
                if st.button("Cerrar Sesión", use_container_width=True, key="btn_admin_cerrar_sesion"):
                    st.session_state.is_admin = False
                    if 'saturday_offset' in st.session_state:
                        del st.session_state.saturday_offset
                    st.rerun()

                st.markdown("<div style='margin-top:0.8rem; margin-bottom:0.8rem; border-top:1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
                if st.button("Sincronizar con SharePoint", use_container_width=True, key="btn_admin_sincronizar_sp"):
                    st.session_state["force_refresh_personal"] = True
                    c_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
                    if os.path.exists(c_dir):
                        for f_name in os.listdir(c_dir):
                            try:
                                os.remove(os.path.join(c_dir, f_name))
                            except Exception:
                                pass
                    dp._open_consolidado_conexion.clear()
                    dp._get_base_shifts_df.clear()
                    dp._open_consolidado_personal.clear()
                    dp.load_supernumeraries.clear()
                    dp.load_modifications.clear()
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    cargar_datos_fn(reload_personal=True)
                    st.success("Datos resincronizados directamente con SharePoint.", icon=":material/check_circle:")
                    st.rerun()

                with st.expander("🛠️ Purgar Modificaciones en SharePoint", expanded=False):
                    st.markdown("Vaciar las modificaciones acumuladas en la Lista de SharePoint (`MODIFICACIONES_SABADOS`).")
                    if gc.is_sharepoint_configured():
                        try:
                            current_items = gc.get_sharepoint_list_items("modificaciones_sabados")
                            total_items = len(current_items)
                        except Exception:
                            current_items = []
                            total_items = 0

                        st.info(f"Modificaciones acumuladas: **{total_items}**")
                        if total_items > 0:
                            json_bytes = json.dumps(current_items, ensure_ascii=False, indent=2).encode('utf-8')
                            timestamp_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            st.download_button(
                                label="📥 Descargar Respaldo JSON",
                                data=json_bytes,
                                file_name=f"sharepoint_modificaciones_backup_{timestamp_now}.json",
                                mime="application/json",
                                use_container_width=True,
                                key="btn_descargar_respaldo_json"
                            )

                        confirm_purge = st.checkbox("Confirmar purga completa", key="chk_confirmar_purga_sp")
                        if st.button("🧹 Purgar y Reiniciar", type="primary", disabled=(not confirm_purge or total_items == 0), use_container_width=True, key="btn_confirmar_purga_sp"):
                            with st.spinner("Purgando en SharePoint..."):
                                item_ids = [str(it.get("_item_id", it.get("id"))) for it in current_items if it.get("_item_id", it.get("id"))]
                                deleted_count = 0
                                if item_ids:
                                    deleted_count = gc.delete_sharepoint_list_items_batch("modificaciones_sabados", item_ids)

                                c_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
                                if os.path.exists(c_dir):
                                    for f_name in os.listdir(c_dir):
                                        try:
                                            os.remove(os.path.join(c_dir, f_name))
                                        except Exception:
                                            pass

                                dp._open_consolidado_conexion.clear()
                                dp._get_base_shifts_df.clear()
                                dp._open_consolidado_personal.clear()
                                dp.load_supernumeraries.clear()
                                dp.load_modifications.clear()
                                st.cache_data.clear()
                                st.cache_resource.clear()
                                cargar_datos_fn(reload_personal=True)
                                st.success(f"{deleted_count} modificaciones eliminadas de SharePoint.", icon=":material/check_circle:")
                                st.rerun()
                    else:
                        st.warning("SharePoint no configurado.")
            else:
                admin_password = "C3ntr4l1234.*"
                try:
                    if "admin_password" in st.secrets:
                        admin_password = st.secrets["admin_password"]
                    elif "azure" in st.secrets and "admin_password" in st.secrets["azure"]:
                        admin_password = st.secrets["azure"]["admin_password"]
                except Exception:
                    pass

                if 'pwd_error' not in st.session_state:
                    st.session_state.pwd_error = None

                def on_pwd_enter():
                    val = st.session_state.admin_pwd_popover
                    if val == admin_password:
                        st.session_state.is_admin = True
                        if 'saturday_offset' in st.session_state:
                            del st.session_state.saturday_offset
                        st.session_state.pwd_error = None
                    else:
                        st.session_state.pwd_error = "Contraseña incorrecta"
                        st.session_state.admin_pwd_popover = ""

                st.text_input(
                    "Contraseña", 
                    type="password", 
                    key="admin_pwd_popover", 
                    on_change=on_pwd_enter
                )
                
                st.button(
                    "Iniciar Sesión", 
                    use_container_width=True, 
                    type="primary",
                    key="btn_admin_iniciar_sesion",
                    on_click=on_pwd_enter
                )
                        
                if st.session_state.pwd_error:
                    st.error(st.session_state.pwd_error)


def renderizar_banner_titulo():
    """Renderiza el banner institucional con gradiente 'Turnos Sábados'."""
    st.markdown("""
        <div class="premium-gradient-banner">
            <div class="premium-banner-icon">
                <i class="bi bi-calendar3"></i>
            </div>
            <div class="premium-banner-text">
                <h1>Turnos Sábados</h1>
                <p>Secuencia sabados</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def renderizar_aviso_informativo():
    """Renderiza la tarjeta informativa de contacto para solicitud de cambios."""
    st.markdown("""
        <div class="info-notice-card">
            Cualquier solicitud de cambio de turno o cambio de secuencia, favor enviar correo a 
            <a href="mailto:central@unionsaludvida.com">central@unionsaludvida.com</a>. 
            Una vez sea aceptado por el correo, se verá reflejado en este cuadro.
        </div>
    """, unsafe_allow_html=True)
