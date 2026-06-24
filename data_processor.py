"""
data_processor.py — adaptado para SharePoint/OneDrive
------------------------------------------------------
Los dos archivos delta (MODIFICACIONES_SABADOS y MODIFICACIONES_PERSONAL) se leen y
escriben en SharePoint mediante graph_client.py.

El archivo maestro (TURNOS SABADOS.xlsx) sigue siendo de SOLO LECTURA: se descarga
por Graph API solo para cargar los turnos base, igual que en el despliegue anterior.

Cuando se ejecuta en local sin credenciales Azure configuradas, usa rutas de archivo
locales como fallback (comportamiento original).
"""

import pandas as pd
import streamlit as st
import openpyxl
import re
import datetime
import os
import io

# ---------------------------------------------------------------------------
# Importación condicional del cliente de Graph API
# ---------------------------------------------------------------------------
try:
    import graph_client as gc
    _USE_SHAREPOINT = gc.is_sharepoint_configured()
except Exception:
    _USE_SHAREPOINT = False

MONTH_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'mrazo': 3,
    'abril': 4, 'mayo': 5, 'junio': 6, 'juniode': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'setiembre': 9,
    'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

MONTH_NAMES_SP = {
    1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
    5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
    9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
}

# ---------------------------------------------------------------------------
# Helpers de acceso a los archivos delta (SharePoint o local)
# ---------------------------------------------------------------------------

def _get_modifications_path(main_excel_path):
    return os.path.join(os.path.dirname(main_excel_path), "MODIFICACIONES_SABADOS.xlsx")

def _get_personal_modifications_path(main_excel_path):
    return os.path.join(os.path.dirname(main_excel_path), "MODIFICACIONES_PERSONAL.xlsx")


def _load_wb_delta(file_key: str, local_path: str, sheet_title: str, cols: list):
    """
    Carga el workbook del archivo delta.
    - En SharePoint: descarga a BytesIO.
    - En local: abre desde disco; si no existe, lo crea.
    Devuelve (wb, ws).
    """
    if _USE_SHAREPOINT:
        try:
            buf = gc.download_excel(file_key)
            wb = openpyxl.load_workbook(buf)
            ws = wb[sheet_title]
            return wb, ws
        except Exception:
            # Archivo aún no existe en SharePoint → crear uno vacío en memoria
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = sheet_title
            ws.append(cols)
            return wb, ws
    else:
        if not os.path.exists(local_path):
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = sheet_title
            ws.append(cols)
            wb.save(local_path)
            wb.close()
        wb = openpyxl.load_workbook(local_path)
        ws = wb[sheet_title]
        return wb, ws


def _save_wb_delta(wb: openpyxl.Workbook, file_key: str, local_path: str):
    """
    Guarda el workbook del archivo delta.
    - En SharePoint: serializa a BytesIO y sube.
    - En local: guarda en disco.
    """
    if _USE_SHAREPOINT:
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        gc.upload_excel(file_key, buf)
        wb.close()
    else:
        wb.save(local_path)
        wb.close()


def _read_delta_df(file_key: str, local_path: str, sheet_title: str, cols: list) -> pd.DataFrame:
    """
    Lee el DataFrame del archivo delta (SharePoint o local).
    Si no existe devuelve DataFrame vacío con las columnas esperadas.
    """
    if _USE_SHAREPOINT:
        try:
            buf = gc.download_excel(file_key)
            df = pd.read_excel(buf, sheet_name=sheet_title)
            for c in cols:
                if c not in df.columns:
                    df[c] = None
            return df[cols].copy()
        except Exception:
            return pd.DataFrame(columns=cols)
    else:
        if not os.path.exists(local_path):
            return pd.DataFrame(columns=cols)
        try:
            df = pd.read_excel(local_path, sheet_name=sheet_title)
            for c in cols:
                if c not in df.columns:
                    df[c] = None
            return df[cols].copy()
        except Exception:
            return pd.DataFrame(columns=cols)


# ---------------------------------------------------------------------------
# Parsers de fechas (sin cambios)
# ---------------------------------------------------------------------------

def clean_month_year(header_str):
    if not isinstance(header_str, str):
        return None, None, None
    header_str = header_str.strip().lower()
    header_str = header_str.replace("mes:", "").replace(" de ", " ").strip()
    header_str = re.sub(r'\s+', ' ', header_str)
    parts = header_str.split(' ')
    if len(parts) >= 2:
        month_word = parts[0]
        year_str = parts[-1]
        month = MONTH_MAP.get(month_word, None)
        try:
            year = int(year_str)
            return month, year, month_word.upper()
        except ValueError:
            return None, None, None
    return None, None, None


def parse_date_cell(cell, expected_month, expected_year):
    if pd.isna(cell):
        return None
    if isinstance(cell, datetime.datetime):
        if cell.month == expected_month and cell.year == expected_year:
            return cell.date()
        if cell.day == expected_month and cell.year == expected_year:
            try:
                return datetime.date(expected_year, expected_month, cell.month)
            except Exception:
                pass
        return cell.date()
    cell_str = str(cell).strip().lower()
    if not cell_str or cell_str == '\xa0':
        return None
    match_slash = re.match(r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$', cell_str)
    if match_slash:
        d, m, y = int(match_slash.group(1)), int(match_slash.group(2)), int(match_slash.group(3))
        if m != expected_month and d == expected_month:
            d, m = m, d
        try:
            return datetime.date(y, m, d)
        except ValueError:
            pass
    cell_str = re.sub(r'\s+', ' ', cell_str)
    day_match = re.search(r'\b(\d{1,2})\b', cell_str)
    if day_match:
        day = int(day_match.group(1))
        month = expected_month
        for m_name, m_val in MONTH_MAP.items():
            if m_name in cell_str:
                month = m_val
                break
        year = expected_year
        year_match = re.search(r'\b(202\d)\b', cell_str)
        if year_match:
            year = int(year_match.group(1))
        try:
            return datetime.date(year, month, day)
        except ValueError:
            pass
    return None


def parse_flat_date(cell):
    if pd.isna(cell):
        return None
    if isinstance(cell, datetime.datetime):
        return cell.date()
    if isinstance(cell, datetime.date):
        return cell
    cell_str = str(cell).strip()
    if not cell_str or cell_str == '\xa0':
        return None
    match_iso = re.match(r'^(\d{4})[/-](\d{1,2})[/-](\d{1,2})', cell_str)
    if match_iso:
        try:
            return datetime.date(int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3)))
        except ValueError:
            pass
    match_slash = re.match(r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})', cell_str)
    if match_slash:
        try:
            return datetime.date(int(match_slash.group(3)), int(match_slash.group(2)), int(match_slash.group(1)))
        except ValueError:
            pass
    try:
        return pd.to_datetime(cell_str).date()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# MODIFICACIONES_PERSONAL
# ---------------------------------------------------------------------------

_COLS_PERSONAL = ['ID', 'CEDULA', 'NOMBRES_Y_APELLIDOS', 'CARGO', 'CELULAR',
                  'SEDE_CECO', 'STATUS', 'TYPE', 'FECHA_INICIO', 'OBSERVACIONES']
_SHEET_PERSONAL = 'MODIFICACIONES_PERSONAL'
_KEY_PERSONAL   = 'modificaciones_personal'


def load_personal_modifications(excel_path):
    local_path = _get_personal_modifications_path(excel_path)
    df = _read_delta_df(_KEY_PERSONAL, local_path, _SHEET_PERSONAL, _COLS_PERSONAL)

    if df.empty:
        return df

    df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
    df['CEDULA'] = df['CEDULA'].astype(str).str.strip()
    df['NOMBRES_Y_APELLIDOS'] = df['NOMBRES_Y_APELLIDOS'].fillna('').astype(str).str.strip().str.upper()
    df['CARGO'] = df['CARGO'].fillna('').astype(str).str.strip().str.upper()
    df['CELULAR'] = df['CELULAR'].fillna('').astype(str).str.strip()
    df['SEDE_CECO'] = df['SEDE_CECO'].fillna('').astype(str).str.strip().str.upper()
    df['STATUS'] = df['STATUS'].fillna('ACTIVO').astype(str).str.strip().str.upper()
    df['TYPE'] = df['TYPE'].astype(str).str.strip().str.upper()
    df['FECHA_INICIO'] = pd.to_datetime(df['FECHA_INICIO'], errors='coerce').dt.date
    df['OBSERVACIONES'] = df['OBSERVACIONES'].fillna('').astype(str).str.strip()
    return df.sort_values(by='ID')


def save_personal_modification(excel_path, personal_data):
    local_path = _get_personal_modifications_path(excel_path)
    wb, ws = _load_wb_delta(_KEY_PERSONAL, local_path, _SHEET_PERSONAL, _COLS_PERSONAL)

    # Asegurar columnas nuevas en el encabezado
    header = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    if 'FECHA_INICIO' not in header:
        ws.cell(row=1, column=ws.max_column + 1).value = 'FECHA_INICIO'
    if 'OBSERVACIONES' not in header:
        ws.cell(row=1, column=ws.max_column + 1).value = 'OBSERVACIONES'

    max_id = 0
    for r in range(2, ws.max_row + 1):
        val = ws.cell(row=r, column=1).value
        if val is not None:
            try:
                max_id = max(max_id, int(val))
            except ValueError:
                pass
    next_id = max_id + 1

    fecha_inicio = personal_data.get('fecha_inicio', None)
    if isinstance(fecha_inicio, (datetime.date, datetime.datetime)):
        fecha_inicio = fecha_inicio.strftime('%Y-%m-%d')
    elif fecha_inicio:
        fecha_inicio = str(fecha_inicio)
    else:
        fecha_inicio = ''

    ws.append([
        next_id,
        str(personal_data.get('cedula', '')).strip(),
        str(personal_data.get('nombres_y_apellidos', '')).strip().upper(),
        str(personal_data.get('cargo', '')).strip().upper(),
        str(personal_data.get('celular', '')).strip(),
        str(personal_data.get('sede_ceco', '')).strip().upper(),
        str(personal_data.get('status', 'ACTIVO')).strip().upper(),
        str(personal_data.get('type', 'AGREGAR')).strip().upper(),
        fecha_inicio,
        str(personal_data.get('observaciones', '')).strip()
    ])

    _save_wb_delta(wb, _KEY_PERSONAL, local_path)
    return next_id


# ---------------------------------------------------------------------------
# MODIFICACIONES_SABADOS
# ---------------------------------------------------------------------------

_COLS_SABADOS = ['ID', 'SHEET', 'DATE', 'ORIGINAL_NAME', 'NEW_NAME',
                 'ROW', 'COL', 'TYPE', 'OBSERVACIONES', 'CLASIFICACION']
_SHEET_SABADOS = 'MODIFICACIONES'
_KEY_SABADOS   = 'modificaciones_sabados'


def load_modifications(excel_path):
    local_path = _get_modifications_path(excel_path)
    df = _read_delta_df(_KEY_SABADOS, local_path, _SHEET_SABADOS, _COLS_SABADOS)

    if df.empty:
        return df

    df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.date
    df['SHEET'] = df['SHEET'].astype(str).str.strip()
    df['ORIGINAL_NAME'] = df['ORIGINAL_NAME'].fillna('').astype(str).str.strip().str.upper()
    df['NEW_NAME'] = df['NEW_NAME'].fillna('').astype(str).str.strip().str.upper()
    df['ROW'] = pd.to_numeric(df['ROW'], errors='coerce').fillna(0).astype(int)
    df['COL'] = pd.to_numeric(df['COL'], errors='coerce').fillna(0).astype(int)
    df['TYPE'] = df['TYPE'].astype(str).str.strip().str.upper()
    df['OBSERVACIONES'] = df['OBSERVACIONES'].fillna('').astype(str).str.strip()
    df['CLASIFICACION'] = df['CLASIFICACION'].fillna('Secuencia Normal').astype(str).str.strip()
    return df.sort_values(by='ID')


def save_modification(excel_path, mod_data):
    local_path = _get_modifications_path(excel_path)
    wb, ws = _load_wb_delta(_KEY_SABADOS, local_path, _SHEET_SABADOS, _COLS_SABADOS)

    header = [ws.cell(row=1, column=c).value for c in range(1, ws.max_column + 1)]
    if 'OBSERVACIONES' not in header:
        ws.cell(row=1, column=ws.max_column + 1).value = 'OBSERVACIONES'
        header.append('OBSERVACIONES')
    if 'CLASIFICACION' not in header:
        ws.cell(row=1, column=ws.max_column + 1).value = 'CLASIFICACION'
        header.append('CLASIFICACION')

    max_id = 0
    for r in range(2, ws.max_row + 1):
        val = ws.cell(row=r, column=1).value
        if val is not None:
            try:
                max_id = max(max_id, int(val))
            except ValueError:
                pass
    next_id = max_id + 1

    date_val = mod_data['date']
    if isinstance(date_val, (datetime.date, datetime.datetime)):
        date_val = date_val.strftime('%Y-%m-%d')

    val_map = {
        'ID': next_id,
        'SHEET': mod_data['sheet'],
        'DATE': date_val,
        'ORIGINAL_NAME': mod_data.get('original_name', '').strip().upper(),
        'NEW_NAME': mod_data.get('new_name', '').strip().upper(),
        'ROW': mod_data.get('row', 0),
        'COL': mod_data.get('col', 0),
        'TYPE': mod_data['type'].strip().upper(),
        'OBSERVACIONES': mod_data.get('observaciones', '').strip(),
        'CLASIFICACION': mod_data.get('clasificacion', 'Secuencia Normal').strip()
    }

    row_data = [val_map.get(col_name, '') for col_name in header]
    ws.append(row_data)

    _save_wb_delta(wb, _KEY_SABADOS, local_path)
    return next_id


# ---------------------------------------------------------------------------
# Carga del Excel maestro (solo lectura — igual que el despliegue anterior)
# ---------------------------------------------------------------------------

def _open_master_excel(excel_path):
    """
    Devuelve un pd.ExcelFile del Excel maestro (TURNOS SABADOS.xlsx).
    En SharePoint: descarga con el drive/file ID del maestro.
    En local: abre desde la ruta directamente.
    """
    if _USE_SHAREPOINT:
        try:
            buf = gc.download_excel("turnos_sabados")
            return pd.ExcelFile(buf)
        except Exception as e:
            raise FileNotFoundError(f"No se pudo descargar el Excel maestro desde SharePoint: {e}")
    else:
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"El archivo Excel no existe en: {excel_path}")
        return pd.ExcelFile(excel_path)


@st.cache_data(ttl=3600, show_spinner=False)
def _get_base_shifts_df(excel_path):
    xl = _open_master_excel(excel_path)

    months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
              'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

    candidate_sheets = []
    for s in xl.sheet_names:
        s_upper = s.upper()
        if s_upper in ["SABADOS 2025", "SABADOS 2026"]:
            candidate_sheets.append(s)
        elif any(m in s_upper for m in months) and re.search(r'\b(202\d)\b', s_upper):
            if not s_upper.startswith("TABLA") and "EXTRA" not in s_upper:
                candidate_sheets.append(s)

    all_shifts = []
    errors = []

    for sheet_name in candidate_sheets:
        df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
        if len(df) == 0:
            continue

        header_row_idx = None
        sabado_col_idx = None
        super_col_idx = None

        for r_idx in range(min(5, len(df))):
            row_vals = [str(val).strip().upper() for val in df.iloc[r_idx] if pd.notna(val)]
            if 'SABADO' in row_vals and 'SUPERNUMERARIO' in row_vals:
                header_row_idx = r_idx
                for c_idx, val in enumerate(df.iloc[r_idx]):
                    if pd.notna(val):
                        val_str = str(val).strip().upper()
                        if val_str == 'SABADO':
                            sabado_col_idx = c_idx
                        elif val_str == 'SUPERNUMERARIO':
                            super_col_idx = c_idx
                break

        if header_row_idx is not None and sabado_col_idx is not None and super_col_idx is not None:
            month_header = sheet_name.split(' ')[0].upper()
            for idx in range(header_row_idx + 1, len(df)):
                row = df.iloc[idx]
                date_cell = row[sabado_col_idx]
                name_cell = row[super_col_idx]
                if pd.notna(date_cell) and pd.notna(name_cell):
                    d = parse_flat_date(date_cell)
                    name_str = str(name_cell).strip().upper()
                    name_str = re.sub(r'\s+', ' ', name_str)
                    if name_str and name_str not in ["VALENCIA", "MES:", "SABADOS", "TOTAL", "CANTIDAD"]:
                        if not name_str.replace('.', '', 1).isdigit() and len(name_str) > 3:
                            if d:
                                all_shifts.append({
                                    'Sheet': sheet_name, 'Month_Header': month_header,
                                    'Date': d, 'Year': d.year, 'Month': d.month,
                                    'Supernumerary': name_str,
                                    'Excel_Row': int(idx + 1),
                                    'Excel_Col': int(super_col_idx + 1),
                                    'Header_Row': int(header_row_idx + 1)
                                })
                            else:
                                errors.append(f"No se pudo parsear la fecha en fila {idx+1} de {sheet_name}")

        elif sheet_name.upper() in ["SABADOS 2025", "SABADOS 2026"]:
            current_month_num = None
            current_year = None
            current_month_name = None
            date_cols = {}
            header_row_idx = None
            i = 0
            n_rows = len(df)
            while i < n_rows:
                row = df.iloc[i]
                is_header = False
                header_val = None
                for val in row:
                    if isinstance(val, str) and "MES:" in val:
                        is_header = True
                        header_val = val
                        break
                if is_header:
                    current_month_num, current_year, current_month_name = clean_month_year(header_val)
                    header_row_idx = i
                    i += 1
                    if i >= n_rows:
                        break
                    date_row = df.iloc[i]
                    date_cols = {}
                    for col_idx, val in enumerate(date_row):
                        if pd.notna(val):
                            d = parse_date_cell(val, current_month_num, current_year)
                            if d:
                                date_cols[col_idx] = d
                            else:
                                val_str = str(val).strip()
                                if val_str and val_str != '\xa0':
                                    errors.append(f"No se pudo parsear fecha '{val_str}' fila {i+1} de {sheet_name}")
                else:
                    if current_month_num is not None:
                        for col_idx, d in date_cols.items():
                            if col_idx < len(row):
                                name = row[col_idx]
                                if pd.notna(name):
                                    name_str = str(name).strip()
                                    name_str = re.sub(r'\s+', ' ', name_str).upper()
                                    if name_str and name_str not in ["VALENCIA", "MES:", "SABADOS", "TOTAL", "CANTIDAD"]:
                                        if not name_str.replace('.', '', 1).isdigit() and len(name_str) > 3:
                                            all_shifts.append({
                                                'Sheet': sheet_name, 'Month_Header': current_month_name,
                                                'Date': d, 'Year': d.year, 'Month': d.month,
                                                'Supernumerary': name_str,
                                                'Excel_Row': int(i + 1),
                                                'Excel_Col': int(col_idx + 1),
                                                'Header_Row': int(header_row_idx + 1)
                                            })
                i += 1

    df_shifts = pd.DataFrame(all_shifts) if all_shifts else pd.DataFrame(columns=[
        'Sheet', 'Month_Header', 'Date', 'Year', 'Month', 'Supernumerary',
        'Excel_Row', 'Excel_Col', 'Header_Row'
    ])
    df_shifts['Excel_Row'] = df_shifts['Excel_Row'].astype(int)
    df_shifts['Excel_Col'] = df_shifts['Excel_Col'].astype(int)
    df_shifts['Observation'] = ''
    df_shifts['Classification'] = 'Secuencia Normal'
    return df_shifts, errors

def load_data(excel_path):
    """
    Lee los turnos del Excel maestro y aplica las modificaciones delta en memoria.
    """
    df_shifts_base, errors_base = _get_base_shifts_df(excel_path)
    df_shifts = df_shifts_base.copy()
    errors = list(errors_base)

    # Aplicar modificaciones delta en memoria
    df_mods = load_modifications(excel_path)

    for _, mod in df_mods.iterrows():
        m_type = mod['TYPE']
        sheet  = mod['SHEET']
        m_date = mod['DATE']
        orig   = mod['ORIGINAL_NAME']
        new    = mod['NEW_NAME']
        row    = mod['ROW']
        col    = mod['COL']

        if m_type == 'REEMPLAZAR':
            obs    = mod.get('OBSERVACIONES', '')
            clasif = mod.get('CLASIFICACION', 'Secuencia Normal')
            if row > 0 and col > 0:
                mask = ((df_shifts['Sheet'] == sheet) &
                        (df_shifts['Excel_Row'] == row) &
                        (df_shifts['Excel_Col'] == col))
                if mask.any():
                    df_shifts.loc[mask, 'Supernumerary'] = new
                    df_shifts.loc[mask, 'Observation']   = obs
                    df_shifts.loc[mask, 'Classification'] = clasif
                else:
                    mask_fb = ((df_shifts['Sheet'] == sheet) &
                               (df_shifts['Date'] == m_date) &
                               (df_shifts['Supernumerary'] == orig))
                    df_shifts.loc[mask_fb, 'Supernumerary'] = new
                    df_shifts.loc[mask_fb, 'Observation']   = obs
                    df_shifts.loc[mask_fb, 'Classification'] = clasif
            else:
                mask = ((df_shifts['Sheet'] == sheet) &
                        (df_shifts['Date'] == m_date) &
                        (df_shifts['Supernumerary'] == orig))
                df_shifts.loc[mask, 'Supernumerary'] = new
                df_shifts.loc[mask, 'Observation']   = obs
                df_shifts.loc[mask, 'Classification'] = clasif

        elif m_type == 'ELIMINAR':
            if row > 0 and col > 0:
                df_shifts = df_shifts[~((df_shifts['Sheet'] == sheet) &
                                        (df_shifts['Excel_Row'] == row) &
                                        (df_shifts['Excel_Col'] == col))]
            else:
                df_shifts = df_shifts[~((df_shifts['Sheet'] == sheet) &
                                        (df_shifts['Date'] == m_date) &
                                        (df_shifts['Supernumerary'] == orig))]

        elif m_type == 'AGREGAR':
            mask = (df_shifts['Date'] == m_date) & (df_shifts['Supernumerary'] == new)
            if mask.any():
                df_shifts.loc[mask, 'Observation'] = mod.get('OBSERVACIONES', '')
                df_shifts.loc[mask, 'Classification'] = mod.get('CLASIFICACION', 'Secuencia Normal')
            else:
                new_row = {
                    'Sheet': sheet,
                    'Month_Header': MONTH_NAMES_SP.get(m_date.month, 'EXTRA'),
                    'Date': m_date, 'Year': m_date.year, 'Month': m_date.month,
                    'Supernumerary': new,
                    'Excel_Row': 0, 'Excel_Col': 0, 'Header_Row': 0,
                    'Observation': mod.get('OBSERVACIONES', ''),
                    'Classification': mod.get('CLASIFICACION', 'Secuencia Normal')
                }
                df_shifts = pd.concat([df_shifts, pd.DataFrame([new_row])], ignore_index=True)

    # Limpieza final de seguridad contra race conditions (múltiples usuarios) o errores en el maestro
    if not df_shifts.empty:
        df_shifts = df_shifts.drop_duplicates(subset=['Date', 'Supernumerary'], keep='last')

    return df_shifts, errors


# ---------------------------------------------------------------------------
# Supernumerarios (solo lectura del maestro + delta personal)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def _get_base_supernumeraries(excel_path):
    try:
        xl = _open_master_excel(excel_path)
        df = pd.read_excel(xl, sheet_name="PERSONAL")
        df.columns = [str(c).strip().upper() for c in df.columns]

        is_super_cargo = df['CARGO'].astype(str).str.upper().str.contains(
            "SUPERNUMERARIO|SUPERNUMERARIA|SUPER", na=False)
        is_super_sede = df['SEDE / CECO'].astype(str).str.upper().str.contains(
            "SUPERNUMERARIOS|SUPERNUMERARIO|SUPER", na=False)
        df_super = df[is_super_cargo | is_super_sede].copy()

        df_super['CEDULA'] = df_super['CEDULA'].apply(
            lambda x: str(int(x)) if pd.notna(x) and str(x).replace('.0', '').isdigit() else str(x))
        df_super['NOMBRES Y APELLIDOS'] = (df_super['NOMBRES Y APELLIDOS']
                                            .astype(str).str.strip().str.upper()
                                            .apply(lambda x: re.sub(r'\s+', ' ', x)))
        df_super['CARGO']      = df_super['CARGO'].astype(str).str.strip().str.upper()
        df_super['SEDE / CECO'] = df_super['SEDE / CECO'].astype(str).str.strip().str.upper()
        df_super['CELULAR']    = df_super['CELULAR'].apply(
            lambda x: str(int(x)) if pd.notna(x) and str(x).replace('.0', '').isdigit() else str(x))
        df_super['CELULAR'] = df_super['CELULAR'].replace('NAN', '')
        df_super['STATUS']  = 'ACTIVO'

        if 'FECHA_INICIO' not in df_super.columns:
            df_super['FECHA_INICIO'] = None
        else:
            df_super['FECHA_INICIO'] = pd.to_datetime(df_super['FECHA_INICIO'], errors='coerce').dt.date
        if 'OBSERVACIONES' not in df_super.columns:
            df_super['OBSERVACIONES'] = ''
        else:
            df_super['OBSERVACIONES'] = df_super['OBSERVACIONES'].fillna('').astype(str).str.strip()
        return df_super
    except Exception as e:
        print(f"Error loading base supernumeraries: {e}")
        return pd.DataFrame(columns=['CEDULA', 'NOMBRES Y APELLIDOS', 'CARGO',
                                     'CELULAR', 'SEDE / CECO', 'FECHA_INICIO', 'OBSERVACIONES', 'STATUS'])

def load_supernumeraries(excel_path):
    df_super = _get_base_supernumeraries(excel_path).copy()
    try:

        df_pm = load_personal_modifications(excel_path)
        for _, mod in df_pm.iterrows():
            m_type   = mod['TYPE']
            cedula   = str(mod['CEDULA']).strip()
            name     = str(mod['NOMBRES_Y_APELLIDOS']).strip().upper()
            cargo    = str(mod['CARGO']).strip().upper()
            celular  = str(mod['CELULAR']).strip()
            sede     = str(mod['SEDE_CECO']).strip().upper()
            status   = str(mod['STATUS']).strip().upper()
            obs      = str(mod.get('OBSERVACIONES', '')).strip()
            fecha_ini = mod.get('FECHA_INICIO', None)

            if m_type in ('AGREGAR', 'MODIFICAR'):
                mask = df_super['CEDULA'] == cedula
                if mask.any():
                    df_super.loc[mask, 'NOMBRES Y APELLIDOS'] = name
                    df_super.loc[mask, 'CARGO']       = cargo
                    df_super.loc[mask, 'CELULAR']     = celular
                    df_super.loc[mask, 'SEDE / CECO'] = sede
                    df_super.loc[mask, 'STATUS']      = status
                    df_super.loc[mask, 'FECHA_INICIO'] = fecha_ini
                    df_super.loc[mask, 'OBSERVACIONES'] = obs
                elif m_type == 'AGREGAR':
                    new_row = pd.DataFrame([{
                        'CEDULA': cedula, 'NOMBRES Y APELLIDOS': name,
                        'CARGO': cargo, 'CELULAR': celular,
                        'SEDE / CECO': sede, 'STATUS': status,
                        'FECHA_INICIO': fecha_ini, 'OBSERVACIONES': obs
                    }])
                    df_super = pd.concat([df_super, new_row], ignore_index=True)
            elif m_type == 'DESACTIVAR':
                mask = df_super['CEDULA'] == cedula
                if mask.any():
                    df_super.loc[mask, 'STATUS'] = 'INACTIVO'

        df_super = df_super[df_super['STATUS'] == 'ACTIVO'].copy()
        return (df_super[['CEDULA', 'NOMBRES Y APELLIDOS', 'CARGO', 'CELULAR',
                           'SEDE / CECO', 'FECHA_INICIO', 'OBSERVACIONES']]
                .sort_values(by='NOMBRES Y APELLIDOS'))
    except Exception as e:
        print(f"Error loading supernumeraries: {e}")
        return pd.DataFrame(columns=['CEDULA', 'NOMBRES Y APELLIDOS', 'CARGO',
                                     'CELULAR', 'SEDE / CECO', 'FECHA_INICIO', 'OBSERVACIONES'])


# ---------------------------------------------------------------------------
# Operaciones de escritura (wrapper sin cambios de firma)
# ---------------------------------------------------------------------------

def update_shift_cell(excel_path, sheet_name, row_idx, col_idx, new_name,
                      date_val=None, observation='', original_name=None,
                      clasificacion='Secuencia Normal'):
    if not date_val:
        df_shifts, _ = load_data(excel_path)
        match = df_shifts[(df_shifts['Sheet'] == sheet_name) &
                          (df_shifts['Excel_Row'] == row_idx) &
                          (df_shifts['Excel_Col'] == col_idx)]
        if not match.empty:
            date_val  = match.iloc[0]['Date']
            orig_name = match.iloc[0]['Supernumerary']
        else:
            date_val  = datetime.date.today()
            orig_name = ""
    else:
        if original_name:
            orig_name = original_name
        else:
            df_shifts, _ = load_data(excel_path)
            match = df_shifts[(df_shifts['Sheet'] == sheet_name) &
                              (df_shifts['Excel_Row'] == row_idx) &
                              (df_shifts['Excel_Col'] == col_idx)]
            orig_name = match.iloc[0]['Supernumerary'] if not match.empty else ""

    if original_name:
        orig_name = original_name

    cleaned_new = str(new_name).strip().upper() if new_name else ""
    mod_data = {
        'sheet': sheet_name, 'date': date_val,
        'original_name': orig_name, 'new_name': cleaned_new,
        'row': row_idx, 'col': col_idx,
        'type': 'ELIMINAR' if not cleaned_new else 'REEMPLAZAR',
        'observaciones': observation, 'clasificacion': clasificacion
    }
    save_modification(excel_path, mod_data)
    return True


def delete_shift_cell(excel_path, sheet_name, row_idx, col_idx,
                      date_val=None, observation='', original_name=None,
                      clasificacion='Secuencia Normal'):
    return update_shift_cell(excel_path, sheet_name, row_idx, col_idx, None,
                             date_val, observation, original_name, clasificacion)


def add_shift_to_date(excel_path, sheet_name, target_date, supernumerary_name,
                      observation='', clasificacion='Secuencia Normal'):
    new_name = str(supernumerary_name).strip().upper()
    if not new_name:
        raise ValueError("El nombre del supernumerario no puede estar vacío.")
    mod_data = {
        'sheet': sheet_name, 'date': target_date,
        'original_name': '', 'new_name': new_name,
        'row': 0, 'col': 0, 'type': 'AGREGAR',
        'observaciones': observation, 'clasificacion': clasificacion
    }
    save_modification(excel_path, mod_data)
    return True


# ---------------------------------------------------------------------------
# Consolidación — NOTA: en modo SharePoint esta función solo limpia los deltas.
# El Excel maestro NO se modifica (es de solo lectura en SharePoint).
# ---------------------------------------------------------------------------

def consolidate_changes_to_excel(excel_path):
    """
    En modo local: escribe los cambios en el Excel maestro y borra los delta.
    En modo SharePoint: los cambios YA están en SharePoint (subidos al guardar cada
    modificación). Esta función solo reinicia los archivos delta para dejar contadores
    en cero, a modo de "confirmación de consolidación".
    """
    df_mods = load_modifications(excel_path)
    df_pm   = load_personal_modifications(excel_path)

    if df_mods.empty and df_pm.empty:
        return True

    if not _USE_SHAREPOINT:
        # Modo local: escritura física en el maestro (código original)
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel maestro no encontrado: {excel_path}")

        wb = openpyxl.load_workbook(excel_path)

        try:
            # --- Personal ---
            if not df_pm.empty and 'PERSONAL' in wb.sheetnames:
                ws_p = wb['PERSONAL']
                headers = [str(cell.value).strip().upper() for cell in ws_p[1]]
                col_map = {
                    'CEDULA': headers.index('CEDULA') + 1 if 'CEDULA' in headers else None,
                    'NOMBRES Y APELLIDOS': headers.index('NOMBRES Y APELLIDOS') + 1 if 'NOMBRES Y APELLIDOS' in headers else None,
                    'CARGO': headers.index('CARGO') + 1 if 'CARGO' in headers else None,
                    'CELULAR': headers.index('CELULAR') + 1 if 'CELULAR' in headers else None,
                    'SEDE / CECO': None,
                    'FECHA RETIRO': headers.index('FECHA RETIRO') + 1 if 'FECHA RETIRO' in headers else None,
                }
                for idx, h in enumerate(headers):
                    if 'SEDE' in h and 'CECO' in h:
                        col_map['SEDE / CECO'] = idx + 1
                        break

                for _, mod in df_pm.iterrows():
                    m_type = mod['TYPE']
                    cedula = str(mod['CEDULA']).strip()
                    name   = str(mod['NOMBRES_Y_APELLIDOS']).strip().upper()
                    cargo  = str(mod['CARGO']).strip().upper()
                    celular = str(mod['CELULAR']).strip()
                    sede   = str(mod['SEDE_CECO']).strip().upper()
                    status = str(mod['STATUS']).strip().upper()

                    found_row_idx = None
                    if col_map['CEDULA']:
                        for r in range(2, ws_p.max_row + 1):
                            cell_val = ws_p.cell(row=r, column=col_map['CEDULA']).value
                            if cell_val is not None:
                                if str(cell_val).replace('.0', '').strip() == cedula.replace('.0', '').strip():
                                    found_row_idx = r
                                    break

                    if m_type == 'AGREGAR':
                        if found_row_idx:
                            if col_map['NOMBRES Y APELLIDOS']: ws_p.cell(row=found_row_idx, column=col_map['NOMBRES Y APELLIDOS']).value = name
                            if col_map['CARGO']:   ws_p.cell(row=found_row_idx, column=col_map['CARGO']).value = cargo
                            if col_map['CELULAR']: ws_p.cell(row=found_row_idx, column=col_map['CELULAR']).value = celular
                            if col_map['SEDE / CECO']: ws_p.cell(row=found_row_idx, column=col_map['SEDE / CECO']).value = sede
                        else:
                            new_row_vals = [None] * len(headers)
                            if col_map['CEDULA']: new_row_vals[col_map['CEDULA']-1] = cedula
                            if col_map['NOMBRES Y APELLIDOS']: new_row_vals[col_map['NOMBRES Y APELLIDOS']-1] = name
                            if col_map['CARGO']:   new_row_vals[col_map['CARGO']-1] = cargo
                            if col_map['CELULAR']: new_row_vals[col_map['CELULAR']-1] = celular
                            if col_map['SEDE / CECO']: new_row_vals[col_map['SEDE / CECO']-1] = sede
                            ws_p.append(new_row_vals)
                    elif m_type == 'DESACTIVAR':
                        if found_row_idx and col_map['FECHA RETIRO']:
                            ws_p.cell(row=found_row_idx, column=col_map['FECHA RETIRO']).value = datetime.date.today().strftime('%Y-%m-%d')

            wb.save(excel_path)
            wb.close()

        except Exception as e:
            try:
                wb.close()
            except Exception:
                pass
            raise e

        # Borrar deltas locales
        for path in [_get_modifications_path(excel_path), _get_personal_modifications_path(excel_path)]:
            if os.path.exists(path):
                os.remove(path)

    else:
        # Modo SharePoint: los archivos delta ya están subidos.
        # Solo los reiniciamos (dejamos solo el encabezado).
        local_dummy = ""

        wb_s = openpyxl.Workbook()
        ws_s = wb_s.active
        ws_s.title = _SHEET_SABADOS
        ws_s.append(_COLS_SABADOS)
        buf_s = io.BytesIO()
        wb_s.save(buf_s)
        gc.upload_excel(_KEY_SABADOS, buf_s)
        wb_s.close()

        wb_p = openpyxl.Workbook()
        ws_p = wb_p.active
        ws_p.title = _SHEET_PERSONAL
        ws_p.append(_COLS_PERSONAL)
        buf_p = io.BytesIO()
        wb_p.save(buf_p)
        gc.upload_excel(_KEY_PERSONAL, buf_p)
        wb_p.close()

    return True