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


if __name__ == "__main__":
    unittest.main()
