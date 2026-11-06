"""
graph_client.py (Puente de Retrocompatibilidad)
-----------------------------------------------
Este archivo sirve como puente para redirigir todas las importaciones
hacia la nueva arquitectura modular en 'modulos.cliente_sharepoint'.
"""

from modulos.cliente_sharepoint import *
from modulos import cliente_sharepoint
