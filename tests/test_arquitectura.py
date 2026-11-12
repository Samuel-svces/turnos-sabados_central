"""
test_arquitectura.py
--------------------
Suite de pruebas automatizadas para validar la refactorización arquitectónica,
la integridad de contratos, la ausencia de código espagueti y la consistencia de estilos.
"""

import sys
import os
import py_compile
import unittest

# Asegurar que el directorio raíz de la aplicación esté en sys.path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)


class TestArquitecturaModular(unittest.TestCase):
    
    def test_01_compilacion_sintaxis(self):
        """Verifica que todos los archivos Python compilen sin errores de sintaxis."""
        archivos = [
            os.path.join(PROJECT_DIR, "app.py"),
            os.path.join(PROJECT_DIR, "data_processor.py"),
            os.path.join(PROJECT_DIR, "graph_client.py"),
            os.path.join(PROJECT_DIR, "ui_dialogs.py"),
            os.path.join(PROJECT_DIR, "styles.py"),
            os.path.join(PROJECT_DIR, "modulos", "procesador_datos.py"),
            os.path.join(PROJECT_DIR, "modulos", "cliente_sharepoint.py"),
            os.path.join(PROJECT_DIR, "componentes", "cabecera.py"),
            os.path.join(PROJECT_DIR, "componentes", "buscador.py"),
            os.path.join(PROJECT_DIR, "componentes", "cuadricula_turnos.py"),
            os.path.join(PROJECT_DIR, "componentes", "dialogos.py"),
            os.path.join(PROJECT_DIR, "estilos", "styles.py"),
        ]
        for f in archivos:
            self.assertTrue(os.path.exists(f), f"Archivo no encontrado: {f}")
            try:
                py_compile.compile(f, doraise=True)
            except py_compile.PyCompileError as e:
                self.fail(f"Fallo de compilación en {f}: {e}")

    def test_02_importacion_modulos_espanol(self):
        """Verifica que los nuevos módulos en español se importen correctamente."""
        try:
            from modulos import procesador_datos
            from modulos import cliente_sharepoint
            from componentes import cabecera
            from componentes import buscador
            from componentes import cuadricula_turnos
            from componentes import dialogos
            from estilos import styles
        except ImportError as e:
            self.fail(f"Fallo al importar módulo en español: {e}")

    def test_03_puentes_retrocompatibilidad(self):
        """Verifica que los archivos puente en la raíz sigan funcionando para código existente."""
        try:
            import data_processor
            import graph_client
            import ui_dialogs
            import styles
            
            # Comprobar funciones delegadas
            self.assertTrue(hasattr(data_processor, "load_data"))
            self.assertTrue(hasattr(graph_client, "is_sharepoint_configured"))
            self.assertTrue(hasattr(ui_dialogs, "show_shift_dialog"))
            self.assertTrue(hasattr(styles, "apply_styles"))
        except ImportError as e:
            self.fail(f"Fallo en puente de retrocompatibilidad: {e}")

    def test_04_contratos_componentes(self):
        """Verifica que las funciones de interfaz exportadas tengan las firmas esperadas."""
        from componentes.cabecera import renderizar_cabecera, renderizar_banner_titulo, renderizar_aviso_informativo
        from componentes.buscador import renderizar_buscador
        from componentes.cuadricula_turnos import renderizar_cuadricula
        from componentes.dialogos import show_shift_dialog, show_add_dialog

        self.assertTrue(callable(renderizar_cabecera))
        self.assertTrue(callable(renderizar_banner_titulo))
        self.assertTrue(callable(renderizar_aviso_informativo))
        self.assertTrue(callable(renderizar_buscador))
        self.assertTrue(callable(renderizar_cuadricula))
        self.assertTrue(callable(show_shift_dialog))
        self.assertTrue(callable(show_add_dialog))

    def test_05_cero_estilos_inline_en_app(self):
        """Verifica que app.py no contenga bloques de estilo <style> inline (espagueti)."""
        app_path = os.path.join(PROJECT_DIR, "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertNotIn("<style>", contenido, "app.py todavía contiene etiquetas <style> inline!")
        self.assertNotIn("</style>", contenido, "app.py todavía contiene etiquetas </style> inline!")

    def test_06_reglas_css_en_styles(self):
        """Verifica que estilos/styles.py contenga todas las clases esenciales."""
        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido = f.read()

        clases_esenciales = [
            "search-highlight-active",
            "search-dimmed",
            "custom-search-marker",
            "topbar-brand",
            "topbar-user-marker",
            "premium-gradient-banner",
            "info-notice-card",
        ]
        for clase in clases_esenciales:
            self.assertIn(clase, contenido, f"Clase CSS '{clase}' no encontrada en estilos/styles.py")

    def test_07_eliminacion_botones_manuales_buscador(self):
        """Verifica que se hayan eliminado los botones manuales B, L, R del buscador."""
        buscador_path = os.path.join(PROJECT_DIR, "componentes", "buscador.py")
        with open(buscador_path, "r", encoding="utf-8") as f:
            contenido = f.read()

        # No deben existir los botones manuales de búsqueda, limpiar y recargar
        self.assertNotIn('key="btn_search"', contenido, "El botón manual de búsqueda no fue eliminado.")
        self.assertNotIn('key="btn_clear"', contenido, "El botón manual de limpiar no fue eliminado.")
        self.assertNotIn('key="btn_refresh"', contenido, "El botón manual de recargar no fue eliminado.")

    def test_08_estandarizacion_identificadores_botones(self):
        """Verifica que los botones tengan nombres e identificadores estandarizados con prefijo btn_."""
        archivos_interfaz = [
            os.path.join(PROJECT_DIR, "app.py"),
            os.path.join(PROJECT_DIR, "componentes", "cabecera.py"),
            os.path.join(PROJECT_DIR, "componentes", "buscador.py"),
            os.path.join(PROJECT_DIR, "componentes", "cuadricula_turnos.py"),
            os.path.join(PROJECT_DIR, "componentes", "dialogos.py")
        ]
        import re
        patron_boton = re.compile(r'st\.button\([^)]*key=["\']([^"\']+)["\']')
        
        for ruta in archivos_interfaz:
            with open(ruta, "r", encoding="utf-8") as f:
                codigo = f.read()
            coincidencias = patron_boton.findall(codigo)
            for key in coincidencias:
                self.assertTrue(key.startswith("btn_"), f"En {os.path.basename(ruta)}, la key de botón '{key}' no sigue la convención estándar 'btn_...'")

    def test_09_buscador_reactivo_eventos_js(self):
        """Verifica que componentes/buscador.py contenga el listener reactivo para el evento 'input'."""
        buscador_path = os.path.join(PROJECT_DIR, "componentes", "buscador.py")
        with open(buscador_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("inputBuscador.addEventListener('input'", contenido, "Falta el listener reactivo 'input' en buscador.py")
        self.assertIn("aplicarResaltadoEnVivo", contenido, "Falta la función de resaltado dinámico en buscador.py")
        self.assertIn("search-highlight-active", contenido, "Falta la clase de marcado activo en buscador.py")

    def test_10_funciones_procesador_datos(self):
        """Verifica la funcionalidad de utilidades básicas en modulos/procesador_datos.py."""
        from modulos import procesador_datos as dp
        self.assertEqual(dp.normalize_name_no_accents("MARÍA JOSÉ"), "MARIA JOSE")
        self.assertEqual(dp.normalize_name_no_accents("Álvaro Gómez"), "ALVARO GOMEZ")
        self.assertIn(1, dp.MONTH_NAMES_SP)
        self.assertEqual(dp.MONTH_NAMES_SP[1], "ENERO")

    def test_11_encabezados_modo_normal_f0fbfb(self):
        """Verifica que los encabezados de fecha en modo normal tengan estilo #F0FBFB y tipografía Outfit."""
        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido = f.read()

        self.assertIn('btn_ordenar_pub', contenido, "No se encontró el selector de botón de ordenar público en styles.py")
        self.assertIn('#F0FBFB', contenido, "El color pastel #F0FBFB no está configurado en styles.py")
        self.assertIn('#ccebee', contenido, "El borde #ccebee no está configurado en styles.py")
        self.assertIn('#17243D', contenido, "El color de texto #17243D no está configurado en styles.py")

    def test_12_boton_deshacer_estilo_f0fbfb(self):
        """Verifica que el botón de deshacer esté en buscador.py y tenga estilo #F0FBFB y solo flecha."""
        buscador_path = os.path.join(PROJECT_DIR, "componentes", "buscador.py")
        with open(buscador_path, "r", encoding="utf-8") as f:
            contenido_b = f.read()
        self.assertIn('btn_deshacer_ultimo_cambio', contenido_b, "El botón deshacer debe estar en buscador.py")

        app_path = os.path.join(PROJECT_DIR, "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            contenido_app = f.read()
        self.assertNotIn('key="btn_deshacer_ultimo_cambio"', contenido_app, "El botón deshacer no debe estar duplicado en app.py")

        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido_s = f.read()
        self.assertIn('btn_deshacer_ultimo_cambio', contenido_s, "Estilo de btn_deshacer_ultimo_cambio no encontrado en styles.py")
        self.assertIn('%230f9a9b', contenido_s, "Flecha SVG no configurada para botón deshacer")

    def test_13_supresion_manage_app_cloud(self):
        """Verifica que estilos/styles.py y app.py contengan reglas para ocultar 'Manage app' de Streamlit Cloud."""
        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido_s = f.read()
        self.assertIn('manage-app-button', contenido_s, "Falta selector manage-app-button en styles.py")
        self.assertIn('stAppDeployButton', contenido_s, "Falta selector stAppDeployButton en styles.py")

        app_path = os.path.join(PROJECT_DIR, "app.py")
        with open(app_path, "r", encoding="utf-8") as f:
            contenido_a = f.read()
        self.assertIn('manage-app-button', contenido_a, "Falta supresión activa de manage-app-button en app.py")

    def test_14_filtro_excel_atomico_form(self):
        """Verifica que el menú Excel use st.form para evitar reejecuciones lentas por cada casilla pulsada."""
        cuadricula_path = os.path.join(PROJECT_DIR, "componentes", "cuadricula_turnos.py")
        with open(cuadricula_path, "r", encoding="utf-8") as f:
            contenido_c = f.read()
        self.assertIn('form_filtro_', contenido_c, "El menú de filtro Excel debe usar st.form para evitar lentitud por cada checkbox")
        self.assertIn('st.form_submit_button', contenido_c, "El menú de filtro Excel debe usar st.form_submit_button para aplicar en un lote único")

    def test_15_optimizacion_drag_drop_y_busqueda(self):
        """Verifica la eliminación de doble ejecución en Drag & Drop y el filtrado suave a 60fps."""
        buscador_path = os.path.join(PROJECT_DIR, "componentes", "buscador.py")
        with open(buscador_path, "r", encoding="utf-8") as f:
            contenido_b = f.read()
        self.assertIn('requestAnimationFrame', contenido_b, "El buscador reactivo debe usar requestAnimationFrame para escritura instantánea")
        self.assertIn('sincronizarBusquedaConStreamlit', contenido_b, "El buscador debe sincronizar automáticamente sin obligar al usuario a presionar Enter")
        self.assertIn('mostrarIndicadorCargaPanel', contenido_b, "Drag & Drop debe tener indicador visual inmediato para evitar sensación de congelamiento")

    def test_16_estilos_login_admin(self):
        """Verifica que los botones de Administrador tengan el color #1F5FD1 y el campo de contraseña tenga borde limpio."""
        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido_s = f.read()
        self.assertIn('#1F5FD1', contenido_s, "Falta el color azul #1F5FD1 en styles.py")
        self.assertIn('btn_admin_iniciar_sesion', contenido_s, "Falta selector btn_admin_iniciar_sesion en styles.py")
        self.assertIn('btn_admin_cerrar_sesion', contenido_s, "Falta selector btn_admin_cerrar_sesion en styles.py")
        self.assertIn('btn_admin_sincronizar_sp', contenido_s, "Falta selector btn_admin_sincronizar_sp en styles.py")
        self.assertIn('admin_pwd_popover', contenido_s, "Falta selector admin_pwd_popover en styles.py")

        cabecera_path = os.path.join(PROJECT_DIR, "componentes", "cabecera.py")
        with open(cabecera_path, "r", encoding="utf-8") as f:
            contenido_c = f.read()
        self.assertNotIn('btn_confirmar_purga_sp', contenido_c, "El botón de purga no debe estar en cabecera.py")

    def test_17_color_encabezados_unificado_f0fbfb(self):
        """Verifica que todos los encabezados tengan el color institucional #F0FBFB y que el botón duplicar no afecte encabezados."""
        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido_s = f.read()
        self.assertIn('#F0FBFB', contenido_s, "Falta el color #F0FBFB en styles.py")
        self.assertNotIn('stColumn"]:has(.dup-btn-wrapper) button', contenido_s, "El botón duplicar no debe alterar los botones de toda la columna")

    def test_18_alerta_remover_turno_dos_opciones(self):
        """Verifica que el diálogo de remoción de turno ofrezca 'SOLO_ESTE' y 'DE_AQUI_EN_ADELANTE' y ejecute correctamente."""
        import streamlit as st
        from componentes.dialogos import show_remover_turno_dialog, ejecutar_remocion_turno
        import datetime
        import pandas as pd
        from unittest.mock import patch

        self.assertTrue(callable(show_remover_turno_dialog))
        self.assertTrue(callable(ejecutar_remocion_turno))

        # 1. Verificar presencia de claves en cuadricula_turnos.py y dialogos.py
        cuadricula_path = os.path.join(PROJECT_DIR, "componentes", "cuadricula_turnos.py")
        with open(cuadricula_path, "r", encoding="utf-8") as f:
            contenido_c = f.read()
        self.assertIn('modal_remover_turno', contenido_c, "Falta cola modal_remover_turno en cuadricula_turnos.py")
        self.assertIn('show_remover_turno_dialog', contenido_c, "Falta llamada a show_remover_turno_dialog en cuadricula_turnos.py")

        dialogos_path = os.path.join(PROJECT_DIR, "componentes", "dialogos.py")
        with open(dialogos_path, "r", encoding="utf-8") as f:
            contenido_d = f.read()
        self.assertIn('radio_rem_alcance', contenido_d, "Falta el radio selector elegible radio_rem_alcance en dialogos.py")
        self.assertIn('btn_confirmar_eliminar_turno', contenido_d, "Falta el botón único btn_confirmar_eliminar_turno en dialogos.py")
        self.assertNotIn('btn_cancelar_rem_dialog', contenido_d, "El botón cancelar no debe estar en dialogos.py")

        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido_s = f.read()
        self.assertIn('radio_rem_alcance', contenido_s, "Faltan estilos para radio_rem_alcance en styles.py")
        self.assertIn('btn_confirmar_eliminar_turno', contenido_s, "Faltan estilos para btn_confirmar_eliminar_turno en styles.py")

        # 2. Configurar mock de session_state con 3 sábados para un médico (pasado, actual, futuro)
        date_past = datetime.date(2026, 11, 7)
        date_current = datetime.date(2026, 11, 14)
        date_future = datetime.date(2026, 11, 21)
        doc_test = "DOC DE PRUEBA"

        mock_df = pd.DataFrame([
            {'Sheet': 'SABADOS 2026', 'Date': date_past, 'Supernumerary': doc_test, 'Excel_Row': 1, 'Excel_Col': 1, 'Classification': 'Secuencia Normal', 'Observation': ''},
            {'Sheet': 'SABADOS 2026', 'Date': date_current, 'Supernumerary': doc_test, 'Excel_Row': 2, 'Excel_Col': 1, 'Classification': 'Secuencia Normal', 'Observation': ''},
            {'Sheet': 'SABADOS 2026', 'Date': date_future, 'Supernumerary': doc_test, 'Excel_Row': 3, 'Excel_Col': 1, 'Classification': 'Secuencia Normal', 'Observation': ''},
        ])

        rem_info = {
            'sat_date': date_current,
            'name': doc_test,
            'clasif_actual': 'Secuencia Normal',
            'obs_actual': '',
            'row_excel': 2,
            'col_excel': 1,
            'sheet_excel': 'SABADOS 2026'
        }

        # Prueba A: SOLO_ESTE
        st.session_state.shifts_df = mock_df.copy()
        st.session_state.excel_path = "mock.xlsx"
        with patch("modulos.procesador_datos.save_modifications_batch", return_value=True), \
             patch("streamlit.rerun"):
            ejecutar_remocion_turno(rem_info, scope="SOLO_ESTE")

        df_despues_solo = st.session_state.shifts_df
        # Debe haber eliminado únicamente date_current (quedan past y future)
        self.assertEqual(len(df_despues_solo), 2)
        fechas_restantes = list(df_despues_solo['Date'])
        self.assertIn(date_past, fechas_restantes)
        self.assertNotIn(date_current, fechas_restantes)
        self.assertIn(date_future, fechas_restantes)
        self.assertEqual(st.session_state.last_action['action'], 'ELIMINAR_SIMPLE')

        # Prueba B: DE_AQUI_EN_ADELANTE
        st.session_state.shifts_df = mock_df.copy()
        with patch("modulos.procesador_datos.save_modifications_batch", return_value=True), \
             patch("streamlit.rerun"):
            ejecutar_remocion_turno(rem_info, scope="DE_AQUI_EN_ADELANTE")

        df_despues_adelante = st.session_state.shifts_df
        # Debe haber eliminado date_current y date_future (solo queda date_past)
        self.assertEqual(len(df_despues_adelante), 1)
        self.assertEqual(df_despues_adelante.iloc[0]['Date'], date_past)
        self.assertEqual(st.session_state.last_action['action'], 'ELIMINAR_LOTE')
        self.assertEqual(len(st.session_state.last_action['deleted_items']), 2)

    def test_19_normalizacion_botones_guardar_eliminar(self):
        """Verifica que 'Guardar Cambios' se haya normalizado a 'Guardar', 'Remover Turno' a 'Eliminar', y los estilos de color correspondan."""
        cuadricula_path = os.path.join(PROJECT_DIR, "componentes", "cuadricula_turnos.py")
        with open(cuadricula_path, "r", encoding="utf-8") as f:
            contenido_c = f.read()
        self.assertIn('"Guardar"', contenido_c, "Falta botón 'Guardar' en cuadricula_turnos.py")
        self.assertIn('"Eliminar"', contenido_c, "Falta botón 'Eliminar' en cuadricula_turnos.py")
        self.assertNotIn('"Guardar Cambios"', contenido_c, "No debe existir 'Guardar Cambios' en cuadricula_turnos.py")
        self.assertNotIn('"Remover Turno"', contenido_c, "No debe existir 'Remover Turno' en cuadricula_turnos.py")

        dialogos_path = os.path.join(PROJECT_DIR, "componentes", "dialogos.py")
        with open(dialogos_path, "r", encoding="utf-8") as f:
            contenido_d = f.read()
        self.assertIn('"Guardar"', contenido_d, "Falta botón 'Guardar' en dialogos.py")
        self.assertIn('"Eliminar"', contenido_d, "Falta botón 'Eliminar' en dialogos.py")
        self.assertNotIn('"Guardar Cambios"', contenido_d, "No debe existir 'Guardar Cambios' en dialogos.py")
        self.assertNotIn('"Remover Turno"', contenido_d, "No debe existir 'Remover Turno' en dialogos.py")

        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido_s = f.read()
        self.assertIn('#fff5f5', contenido_s, "Falta el color rojo suave #fff5f5 para botones de eliminar en styles.py")
        self.assertIn('#0f9a9b', contenido_s, "Falta el color institucional #0f9a9b para botones de guardar/acción en styles.py")


if __name__ == "__main__":
    unittest.main()
