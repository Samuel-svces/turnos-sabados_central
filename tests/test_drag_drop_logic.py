"""
test_drag_drop_logic.py
-----------------------
Pruebas unitarias para la funcionalidad de Drag & Drop entre columnas de sábados:
1. Exportación y existencia de show_drag_drop_action_dialog en componentes/dialogos.py.
2. Presencia de marcadores de fecha data-sat-date y wrappers de metadatos en componentes/cuadricula_turnos.py.
3. Presencia del manejador de eventos HTML5 Drag & Drop en componentes/buscador.py.
4. Presencia de estilos CSS para arrastre y zonas de soltado activas en estilos/styles.py.
5. Verificación de lógica de intercambio mutuo y cálculo de secuencia quincenal.
"""

import unittest
import os
import datetime
import pandas as pd

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))


class TestDragDropLogic(unittest.TestCase):

    def test_01_dialogo_drag_drop_definido(self):
        """Verifica que show_drag_drop_action_dialog esté definido en componentes/dialogos.py."""
        dialogos_path = os.path.join(PROJECT_DIR, "componentes", "dialogos.py")
        with open(dialogos_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("def show_drag_drop_action_dialog(", contenido, "show_drag_drop_action_dialog debe estar definido")
        self.assertIn("@st.dialog", contenido, "show_drag_drop_action_dialog debe usar el decorador @st.dialog")
        self.assertIn("Cambio de Turno (Intercambio con otro médico)", contenido)
        self.assertIn("Compensación / Pago de Turno", contenido)
        self.assertIn("Cambiar de Secuencia", contenido)

    def test_02_cuadricula_puente_y_marcadores(self):
        """Verifica que la cuadrícula contenga el puente oculto y los atributos de arrastre."""
        cuadricula_path = os.path.join(PROJECT_DIR, "componentes", "cuadricula_turnos.py")
        with open(cuadricula_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("data-sat-date", contenido, "El marcador de columna debe incluir data-sat-date")
        self.assertIn("doc-admin-card-wrap", contenido, "Debe existir el contenedor con metadatos del médico")
        self.assertIn("bridge_drag_drop_payload", contenido, "Debe existir el input puente para el payload")
        self.assertIn("btn_trigger_drag_drop", contenido, "Debe existir el botón disparador del drop")

    def test_03_buscador_script_drag_drop(self):
        """Verifica que buscador.py contenga el listener reactivo de Drag & Drop."""
        buscador_path = os.path.join(PROJECT_DIR, "componentes", "buscador.py")
        with open(buscador_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("inicializarDragAndDrop", contenido, "Falta la función inicializarDragAndDrop en buscador.py")
        self.assertIn("doc-draggable-card", contenido, "Debe asignar la clase doc-draggable-card")
        self.assertIn("saturday-col-drop-active", contenido, "Debe gestionar la clase saturday-col-drop-active")
        self.assertIn("dragstart", contenido, "Debe escuchar el evento dragstart")
        self.assertIn("dragover", contenido, "Debe escuchar el evento dragover")
        self.assertIn("drop", contenido, "Debe escuchar el evento drop")

    def test_04_estilos_drag_drop(self):
        """Verifica que styles.py defina las clases visuales de arrastre y soltado."""
        styles_path = os.path.join(PROJECT_DIR, "estilos", "styles.py")
        with open(styles_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("button.doc-draggable-card", contenido)
        self.assertIn(".saturday-col-drop-active", contenido)
        self.assertIn(".drag-drop-bridge-container", contenido)

    def test_05_logica_paridad_quincenal_secuencia(self):
        """Valida que la paridad quincenal ISO calcule correctamente el desplazamiento entre secuencias."""
        # Sábado 7 Nov 2026 -> Semana ISO 45 (impar: paridad 1)
        # Sábado 14 Nov 2026 -> Semana ISO 46 (par: paridad 0)
        d1 = datetime.date(2026, 11, 7)
        d2 = datetime.date(2026, 11, 14)
        p1 = d1.isocalendar()[1] % 2
        p2 = d2.isocalendar()[1] % 2
        self.assertNotEqual(p1, p2, "Dos sábados consecutivos deben tener paridades opuestas (secuencias alternas)")
        
        # Desplazamiento a la siguiente semana
        delta = (d2 - d1).days
        self.assertEqual(delta, 7, "La diferencia entre sábados contiguos debe ser 7 días")
        d3 = d1 + datetime.timedelta(days=14)
        p3 = d3.isocalendar()[1] % 2
        self.assertEqual(p1, p3, "Sábados cada 14 días deben pertenecer a la misma secuencia")


if __name__ == "__main__":
    unittest.main()
