"""
graph_client.py
---------------
Capa de acceso a Microsoft Graph API para leer y escribir los archivos
MODIFICACIONES_SABADOS.xlsx y MODIFICACIONES_PERSONAL.xlsx alojados en SharePoint/OneDrive.

Funciones expuestas:
  - download_excel(file_key)  → io.BytesIO  (listo para pd.read_excel / openpyxl.load_workbook)
  - upload_excel(file_key, buffer)           (sube el BytesIO de vuelta a SharePoint)

file_key: "modificaciones_sabados" | "modificaciones_personal"

Credenciales leídas desde st.secrets (Streamlit Cloud) o variables de entorno (local).
"""

import io
import os
import requests
import msal
import streamlit as st


# ---------------------------------------------------------------------------
# Configuración — lee de st.secrets si existe, si no de variables de entorno
# ---------------------------------------------------------------------------

def _cfg(key: str) -> str:
    try:
        return st.secrets["azure"][key]
    except Exception:
        return os.environ.get(key, "")


def _get_access_token() -> str:
    """Obtiene un token de aplicación (client credentials flow)."""
    tenant_id   = _cfg("tenant_id")
    client_id   = _cfg("client_id")
    client_secret = _cfg("client_secret")

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret,
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in result:
        raise RuntimeError(
            f"No se pudo obtener token de Azure AD: {result.get('error_description', result)}"
        )
    return result["access_token"]


def _file_url(file_key: str, action: str = "content") -> str:
    """
    Construye la URL de Graph API para el archivo indicado.
    action: "content"  → descarga/sube el binario
    """
    key_map = {
        "turnos_sabados":         ("drive_id_turnos",  "file_id_turnos"),
        "modificaciones_sabados": ("drive_id_mod_sab", "file_id_mod_sab"),
        "modificaciones_personal": ("drive_id_mod_per", "file_id_mod_per"),
    }
    if file_key not in key_map:
        raise ValueError(f"file_key inválido: {file_key}")

    drive_id_key, file_id_key = key_map[file_key]
    drive_id = _cfg(drive_id_key)
    file_id  = _cfg(file_id_key)

    return f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/{action}"


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def download_excel(file_key: str) -> io.BytesIO:
    """
    Descarga el Excel indicado desde SharePoint/OneDrive.
    Devuelve un BytesIO listo para pasar a pd.read_excel() o openpyxl.load_workbook().
    """
    token = _get_access_token()
    url   = _file_url(file_key, "content")

    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Error al descargar '{file_key}': HTTP {resp.status_code} — {resp.text[:300]}"
        )
    return io.BytesIO(resp.content)


def upload_excel(file_key: str, buffer: io.BytesIO) -> None:
    """
    Sube el BytesIO como el Excel indicado en SharePoint/OneDrive (sobreescribe el archivo).
    """
    token = _get_access_token()
    url   = _file_url(file_key, "content")

    buffer.seek(0)
    content = buffer.read()

    resp = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
        data=content,
        timeout=60,
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Error al subir '{file_key}': HTTP {resp.status_code} — {resp.text[:300]}"
        )


def is_sharepoint_configured() -> bool:
    """Devuelve True si las credenciales de Azure están configuradas."""
    try:
        return bool(_cfg("tenant_id") and _cfg("client_id") and _cfg("client_secret"))
    except Exception:
        return False