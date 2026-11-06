"""
data_processor.py (Puente de Retrocompatibilidad)
-------------------------------------------------
Este archivo sirve como puente para redirigir todas las importaciones
hacia la nueva arquitectura modular en 'modulos.procesador_datos'.
"""

from modulos.procesador_datos import *
from modulos import procesador_datos

# Re-export de funciones internas para compatibilidad de suites de pruebas existentes
_open_consolidado_conexion = getattr(procesador_datos, '_open_consolidado_conexion', None)
_get_base_shifts_df = getattr(procesador_datos, '_get_base_shifts_df', None)
_CACHE_DIR = getattr(procesador_datos, '_CACHE_DIR', None)

