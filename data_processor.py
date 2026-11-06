"""
data_processor.py (Puente de Retrocompatibilidad)
-------------------------------------------------
Este archivo sirve como puente para redirigir todas las importaciones
hacia la nueva arquitectura modular en 'modulos.procesador_datos'.
"""

from modulos.procesador_datos import *
from modulos import procesador_datos
