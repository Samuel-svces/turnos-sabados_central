"""
graph_client.py (Puente de Retrocompatibilidad)
-----------------------------------------------
Este archivo sirve como puente para redirigir todas las importaciones
hacia la nueva arquitectura modular en 'modulos.cliente_sharepoint'.
"""

from modulos.cliente_sharepoint import *
from modulos import cliente_sharepoint

# Re-export de funciones internas para compatibilidad de suites de pruebas existentes
_clean_guid = getattr(cliente_sharepoint, '_clean_guid', None)
_file_urls = getattr(cliente_sharepoint, '_file_urls', None)
_file_url = getattr(cliente_sharepoint, '_file_url', None)
_get_access_token = getattr(cliente_sharepoint, '_get_access_token', None)

