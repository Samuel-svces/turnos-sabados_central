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
import time
import urllib.parse


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


def _file_urls(file_key: str, action: str = "content") -> list:
    """
    Construye las posibles URLs de Graph API para el archivo indicado.
    action: "content" → descarga/sube el binario
            "item"    → consulta metadatos del item
    """
    urls = []
    key_map = {
        "turnos_sabados":         ("drive_id_turnos",  "file_id_turnos"),
        "modificaciones_sabados": ("drive_id_mod_sab", "file_id_mod_sab"),
        "modificaciones_personal": ("drive_id_mod_per", "file_id_mod_per"),
        "consolidado_personal":   ("drive_id_consolidado", "file_id_consolidado"),
    }
    if file_key in key_map:
        drive_id_key, file_id_key = key_map[file_key]
        drive_id = _cfg(drive_id_key)
        file_id  = _cfg(file_id_key)
        if drive_id and file_id:
            if action == "content":
                urls.append(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}/content")
            else:
                urls.append(f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{file_id}")

    if file_key in ("consolidado_personal", "bd_personal"):
        site_domain = "unionsaludvida.sharepoint.com"
        site_rel_path = "/sites/CENTRALDENOVEDADESCONSOLIDADOS"
        candidate_paths = [
            "CONSOLIDADOS/CONSOLIDADO 2026/CONSOLIDADO 2026.xlsx",
            "Documentos compartidos/CONSOLIDADOS/CONSOLIDADO 2026/CONSOLIDADO 2026.xlsx"
        ]
        for cpath in candidate_paths:
            item_path = urllib.parse.quote(cpath, safe='/')
            base_url = f"https://graph.microsoft.com/v1.0/sites/{site_domain}:{site_rel_path}:/drive/root:/{item_path}"
            if action == "content":
                urls.append(f"{base_url}:/content")
            else:
                urls.append(base_url)

    if not urls:
        raise ValueError(f"file_key inválido: {file_key}")
    return urls


def _file_url(file_key: str, action: str = "content") -> str:
    return _file_urls(file_key, action)[0]


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def download_excel(file_key: str) -> io.BytesIO:
    """
    Descarga el Excel indicado desde SharePoint/OneDrive.
    Devuelve un BytesIO listo para pasar a pd.read_excel() o openpyxl.load_workbook().
    """
    token = _get_access_token()
    urls = _file_urls(file_key, "content")
    last_err = None

    for url in urls:
        try:
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            if resp.status_code == 200:
                return io.BytesIO(resp.content)
            last_err = f"HTTP {resp.status_code} — {resp.text[:300]}"
        except Exception as e:
            last_err = str(e)

    raise RuntimeError(
        f"Error al descargar '{file_key}': {last_err}"
    )


def upload_excel(file_key: str, buffer: io.BytesIO, max_retries: int = 3) -> None:
    """
    Sube el BytesIO como el Excel indicado en SharePoint/OneDrive (sobreescribe el archivo).
    Intenta varias veces si el archivo está bloqueado (HTTP 423).
    """
    token = _get_access_token()
    url   = _file_url(file_key, "content")

    buffer.seek(0)
    content = buffer.read()

    for attempt in range(1, max_retries + 1):
        resp = requests.put(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
            data=content,
            timeout=60,
        )
        
        if resp.status_code in (200, 201):
            return  # Éxito
            
        if resp.status_code == 423:
            if attempt < max_retries:
                time.sleep(2)  # Espera 2 segundos antes de reintentar
                continue
            else:
                raise RuntimeError(
                    f"El archivo '{file_key}' está bloqueado temporalmente por otro usuario o aplicación (HTTP 423). "
                    "Por favor, asegúrate de cerrarlo en Excel, SharePoint o OneDrive y vuelve a intentarlo."
                )
                
        # Si no es éxito ni 423, rompe el ciclo lanzando la excepción
        raise RuntimeError(
            f"Error al subir '{file_key}': HTTP {resp.status_code} — {resp.text[:300]}"
        )


def is_sharepoint_configured() -> bool:
    """Devuelve True si las credenciales de Azure están configuradas."""
    try:
        return bool(_cfg("tenant_id") and _cfg("client_id") and _cfg("client_secret"))
    except Exception:
        return False


def get_file_metadata(file_key: str) -> dict:
    """Obtiene los metadatos de un archivo en SharePoint/OneDrive."""
    token = _get_access_token()
    urls = _file_urls(file_key, "item")
    last_err = None

    for url in urls:
        try:
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            last_err = f"HTTP {resp.status_code} — {resp.text[:300]}"
        except Exception as e:
            last_err = str(e)

    raise RuntimeError(
        f"Error al obtener metadatos de '{file_key}': {last_err}"
    )