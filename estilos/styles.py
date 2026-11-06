# Styles and Custom CSS for TURNOS SABADOS Application

# pyrefly: ignore [missing-import]
import streamlit as st
import textwrap

def apply_styles():
    """
    Injects custom CSS to give the application a premium, modern look.
    """
    css_content = textwrap.dedent("""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --usv-user-initials: "JJ";
    }
    
    /* Global Styles */
    html, body, .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hide the Streamlit top header (hamburger menu) to save space */
    header[data-testid="stHeader"],
    [data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        max-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        visibility: hidden !important;
    }
    
    /* Ocultar completamente la barra lateral (sidebar) y sus controles para que no desplace el contenido */
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    div[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="collapsedControl"] {
        display: none !important;
        width: 0px !important;
        height: 0px !important;
        min-width: 0px !important;
        max-width: 0px !important;
        visibility: hidden !important;
        position: absolute !important;
        pointer-events: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Contenedor principal estilizado como tarjeta unificada premium */
    div[data-testid="stAppViewBlockContainer"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 0px !important;
        box-shadow: none !important;
        margin: 0px !important;
    }
    
    .stApp,
    [data-testid="stAppViewContainer"],
    section.main,
    .stMain,
    div[data-testid="stMain"],
    div[data-testid="stMainBlockContainer"],
    .stMainBlockContainer,
    .block-container {
        padding-top: 0px !important;
        padding-bottom: 2rem !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
        margin-top: 0px !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        max-width: 100% !important;
        width: 100% !important;
        background-color: transparent !important;
        background: transparent !important;
        box-sizing: border-box !important;
    }
    
    @media (min-width: 576px) {
        .stApp,
        [data-testid="stAppViewContainer"],
        section.main,
        .stMain,
        div[data-testid="stMain"],
        div[data-testid="stMainBlockContainer"],
        .stMainBlockContainer,
        .block-container {
            padding-left: 0px !important;
            padding-right: 0px !important;
            padding-top: 0px !important;
            max-width: 100% !important;
            width: 100% !important;
        }
    }
    
    /* Compactar espaciado vertical entre secciones en el contenedor principal */
    div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
        gap: 0.45rem !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Margen lateral para el contenido de la aplicación debajo del topbar */
    div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:not(:has(.topbar-brand)):not(:has(style)):not(:has(.app-topbar-marker)),
    div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stLayoutWrapper"]:not(:has(.topbar-brand)) {
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        box-sizing: border-box !important;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    /* App Background Gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(90, 92, 106, 0.03) 0%, rgba(32, 45, 58, 0.05) 90%);
    }
    
    /* Ocultar marcador superior y contenedores de estilo/marcadores */
    .header-banner-marker,
    .app-topbar-marker,
    div[data-testid="stElementContainer"]:has(style),
    div[data-testid="stElementContainer"]:has(.app-topbar-marker),
    div[data-testid="stElementContainer"]:has(.header-banner-marker),
    div.element-container:has(style),
    div.element-container:has(.app-topbar-marker),
    div.element-container:has(.header-banner-marker) {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    /* Topbar Institucional Superior (Fondo Blanco de esquina a esquina) */
    div[data-testid="stLayoutWrapper"]:has(div[data-testid="stHorizontalBlock"]:has(.topbar-brand)) {
        margin: 0px !important;
        padding: 0px !important;
        width: 100% !important;
        max-width: 100% !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.topbar-brand) {
        background-color: #ffffff !important;
        border-bottom: 1px solid #e2e8f0 !important;
        padding: 0.35rem 1.5rem 0.35rem 1rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        margin-top: -1.25rem !important;
        margin-left: 0px !important;
        margin-right: 0px !important;
        left: 0px !important;
        right: 0px !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="stColumn"] {
        display: flex !important;
        align-items: center !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="stColumn"]:first-of-type,
    div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="column"]:first-of-type {
        justify-content: flex-start !important;
        padding-left: 0px !important;
        margin-left: 0px !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="stColumn"]:last-of-type,
    div[data-testid="stHorizontalBlock"]:has(.topbar-brand) div[data-testid="column"]:last-of-type {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        padding-right: 0px !important;
        margin-right: 0px !important;
        margin-left: auto !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker),
    div[data-testid="stColumn"]:has(.topbar-user-marker) {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        height: 100% !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) > div[data-testid="stVerticalBlock"],
    div[data-testid="stColumn"]:has(.topbar-user-marker) > div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-end !important;
        gap: 0px !important;
        width: 100% !important;
        height: 100% !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stElementContainer"]:has(div[data-testid="stPopover"]),
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stElementContainer"]:has(div[data-testid="stPopover"]) {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        margin: 0 !important;
        padding: 0 !important;
        width: auto !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"],
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Identidad de Marca: Logo + Separador + Conexión operativa */
    .topbar-brand {
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        user-select: none !important;
        padding-left: 0px !important;
        margin-left: 0px !important;
    }
    
    .topbar-logo {
        height: 28px !important;
        max-height: 30px !important;
        width: auto !important;
        object-fit: contain !important;
        display: block !important;
    }
    
    .topbar-brand-divider {
        display: inline-block !important;
        width: 1px !important;
        height: 22px !important;
        background-color: #e2e8f0 !important;
        opacity: 1 !important;
        margin: 0 0.85rem !important;
    }
    
    .topbar-titles {
        display: flex !important;
        align-items: center !important;
    }
    
    .topbar-title {
        font-family: 'Outfit', sans-serif;
        font-size: 21px;
        font-weight: 600;
        color: #0f172a !important;
        letter-spacing: -0.2px !important;
        white-space: nowrap !important;
        -webkit-text-fill-color: #0f172a;
    }
    
    /* Banner institucional degradado de Turnos Sábados recortado */
    div[data-testid="stElementContainer"]:has(.premium-gradient-banner) {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.75rem !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .premium-gradient-banner {
        background: linear-gradient(90deg, #0a2039 0%, #133554 35%, #2a5d78 70%, #4e8b9e 100%) !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.25rem !important;
        display: flex !important;
        align-items: center !important;
        margin: 0px !important;
        box-sizing: border-box !important;
        box-shadow: 0 4px 14px rgba(10, 32, 57, 0.2) !important;
        width: 100% !important;
        gap: 0.85rem !important;
        max-width: 95%;
    }

    .premium-gradient-banner {
    margin-left: 50px !important; 
}
    
    /* Resetear margen, bordes y sombras de alertas y notificaciones y sus contenedores */
    div[data-testid="stElementContainer"]:has(div[data-testid="stAlert"]),
    div[data-testid="stElementContainer"]:has(div[data-testid="stNotification"]),
    div[data-testid="stElementContainer"]:has(div[role="alert"]),
    div.element-container:has(.stAlert),
    div.element-container:has(.stNotification),
    div.element-container:has([role="alert"]) {
        margin: 0px !important;
        padding: 0px !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stNotification"], div[data-testid="stAlert"], .stAlert, div[role="alert"],
    div[data-testid="stNotification"] *, div[data-testid="stAlert"] *, .stAlert *, div[role="alert"] * {
        margin: 0px !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Quitar el borde del panel de pestañas (contenedor exterior) */
    div[data-testid="stTabPanel"],
    div[role="tabpanel"],
    div[data-baseweb="tab-panel"],
    .stTabs > div {
        border: none !important;
        box-shadow: none !important;
    }

    /* Quitar borde alrededor de columnas y bloques verticales del calendario */
    div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="column"] {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.premium-banner-transparent) > div[data-testid="column"] {
        /* Centrar contenido verticalmente y quitar márgenes extra */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Alinear el botón de la tuerca verticalmente centrado y a la derecha */
    div[data-testid="stColumn"]:has(.admin-gear-marker),
    div[data-testid="column"]:has(.admin-gear-marker) {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }
    
    /* Transparent container for title text inside banner */
    .premium-banner-transparent {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        height: 100%;
        padding-left: 2px;
    }

    .premium-banner-icon {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 8px !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        min-height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-right: 0px !important;
        box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.08) !important;
        flex-shrink: 0 !important;
    }
    .premium-banner-icon i {
        color: #ffffff !important;
        font-size: 1.15rem !important;
        line-height: 1 !important;
    }
    .premium-banner-text {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    .premium-banner-text h1 {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.25rem !important;
        margin: 0 !important;
        padding: 0 !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        line-height: 1.15 !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .premium-banner-text p {
        color: rgba(255, 255, 255, 0.8) !important;
        margin: 2px 0 0 0 !important;
        padding: 0 !important;
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.01em !important;
    }
    
    /* Tarjeta informativa de solicitud de cambios - compacta */
    .info-notice-card {
        background-color: #f0fbfb !important;
        border-radius: 10px !important;
        padding: 8px 18px !important;
        text-align: center !important;
        color: #475569 !important;
        font-size: 0.86rem !important;
        line-height: 1.35 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.35rem !important;
        max-width: 60% !important;   
        margin-left: auto !important; 
        margin-right: auto !important;
    }
    .info-notice-card a {
        color: #0284c7 !important;
        font-weight: 700 !important;
        text-decoration: underline !important;
    }
    
    /* Premium Cards (Glassmorphism style) */
    .card-glass {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.45);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        transition: all 0.3s ease-in-out;
        margin-bottom: 1rem;
    }
    
    .card-glass:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.08);
        border-color: rgba(25, 118, 210, 0.3);
    }
    
    /* Custom KPI Cards */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 2rem;
        flex-wrap: wrap;
    }
    
    .kpi-card {
        flex: 1;
        min-width: 180px;
        background: linear-gradient(135deg, rgba(255,255,255,0.8) 0%, rgba(240,244,248,0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 4px 20px 0 rgba(31, 38, 135, 0.03);
        transition: transform 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card:hover {
        transform: scale(1.02);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #1976d2;
    }
    
    .kpi-card.green::before {
        background: #2e7d32;
    }
    
    .kpi-card.purple::before {
        background: #6a1b9a;
    }
    
    .kpi-card.orange::before {
        background: #ef6c00;
    }
    
    .kpi-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #78909c;
        margin-bottom: 0.25rem;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a237e;
        line-height: 1.1;
    }
    
    .kpi-desc {
        font-size: 0.75rem;
        color: #90a4ae;
        margin-top: 0.25rem;
    }
    
    /* Alert cards for duplicates */
    .alert-card-warning {
        background: rgba(255, 243, 205, 0.85);
        border: 1px solid rgba(255, 238, 186, 0.9);
        color: #856404;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.9rem;
    }
    
    /* Calendar Saturday view */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.25rem;
        margin-top: 0px !important;
    }
    
    /* ---- Saturday Column Card Styling ---- */
    div[data-testid="stColumn"]:has(.saturday-col-marker) {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.8rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
        box-sizing: border-box !important;
    }
    
    div[data-testid="stColumn"]:has(.saturday-col-marker):hover {
        border-color: #cbd5e1 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Ocultar el marcador de columna de sábados y fecha */
    div[data-testid="stElementContainer"]:has(.saturday-col-marker),
    div[data-testid="stElementContainer"]:has(.date-header-marker) {
        display: none !important;
        height: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .sat-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: white;
        background-color: #005eb8;
        padding: 0.6rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
        text-align: center;
        border: none;
    }
    
    .sat-header.holiday {
        color: #d32f2f;
        border-bottom-color: #ffcdd2;
    }
    
    .name-badge {
        font-size: 0.8rem;
        background-color: #f1f8e9;
        color: #33691e;
        padding: 0.35rem 0.65rem;
        border-radius: 8px;
        margin-bottom: 0.35rem;
        font-weight: 500;
        text-align: center;
        border: 1px solid #dcedc8;
        word-break: break-word;
        transition: all 0.15s;
        position: relative;
        overflow: visible;
        cursor: default;
    }
    
    .name-badge:hover {
        background-color: #dcedc8;
        transform: scale(1.02);
        z-index: 10;
    }
    
    /* Indicator dot when badge has an observation */
    .name-badge.has-obs::before {
        content: '';
        position: absolute;
        top: -3px;
        right: -3px;
        width: 8px;
        height: 8px;
        background: #1976d2;
        border-radius: 50%;
        border: 1.5px solid white;
        box-shadow: 0 1px 4px rgba(25,118,210,0.4);
    }
    
    /* Tooltip box shown on hover */
    .name-badge.has-obs:hover::after {
        content: attr(data-obs);
        position: absolute;
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
        background: #1e293b;
        color: #e2e8f0;
        font-size: 0.75rem;
        font-weight: 400;
        padding: 0.45rem 0.75rem;
        border-radius: 8px;
        white-space: normal;
        word-break: break-word;
        min-width: 160px;
        max-width: 240px;
        text-align: left;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        z-index: 9999;
        pointer-events: none;
        line-height: 1.4;
        border: 1px solid rgba(255,255,255,0.08);
    }
    
    /* Tooltip arrow */
    .name-badge.has-obs:hover::before {
        content: '';
        position: absolute;
        bottom: calc(100% + 2px);
        left: 50%;
        transform: translateX(-50%);
        border: 5px solid transparent;
        border-top-color: #1e293b;
        width: 0;
        height: 0;
        background: none;
        border-radius: 0;
        box-shadow: none;
        z-index: 9999;
    }
    
    .name-badge.duplicate {
        background-color: #ffebee;
        color: #c62828;
        border-color: #ffcdd2;
        font-weight: 600;
    }
    
    /* Highlight for saturdays with modifications */
    .saturday-col.changed-shift {
        box-shadow: 0 4px 15px rgba(13, 71, 161, 0.08) !important;
    }
    
    .sat-header.changed-shift-header {
        /* Keep it same as normal header to avoid full red column */
    }
    
    .changed-label {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        background-color: #ffcdd2;
        color: #b71c1c;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* ---- Doctor Name Badge with built-in hover tooltip ---- */
    .doc-btn-wrap {
        position: relative;
        width: 100%;
        margin-bottom: 0px;
    }

    /* The clickable name badge */
    .doc-name-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        width: 100%;
        box-sizing: border-box;
        padding: 0.22rem 0.5rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        font-family: 'Plus Jakarta Sans', sans-serif;
        cursor: pointer;
        transition: background 0.18s, border-color 0.18s, transform 0.12s;
        text-align: center;
        word-break: break-word;
        line-height: 1.3;
        /* Default appearance matches Streamlit secondary button */
        background: white;
        color: #262730;
        border: 1px solid rgba(49,51,63,0.2);
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        text-decoration: none;
    }

    /* Badge with observation indicator */
    .doc-name-badge.has-obs {
        border-color: rgba(25,118,210,0.35);
        background: rgba(25,118,210,0.03);
    }

    /* Small blue dot indicator when has obs */
    .doc-name-badge.has-obs .obs-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #1976d2;
        flex-shrink: 0;
        box-shadow: 0 0 4px rgba(25,118,210,0.5);
    }

    .doc-name-badge .obs-dot {
        display: none;
    }

    .doc-name-badge:hover {
        background: #1976d2;
        color: white;
        border-color: #1565c0;
        transform: scale(1.01);
    }

    .doc-name-badge.has-obs:hover {
        background: #1565c0;
        color: white;
    }

    /* Resaltar resultado de búsqueda */
    .doc-name-badge.search-highlight {
        background-color: #fff8e1;
        border-color: #ffc107;
        color: #ff8f00;
        box-shadow: 0 0 12px rgba(255, 193, 7, 0.4);
        transform: scale(1.03);
        z-index: 5;
        font-weight: 700;
    }
    
    .doc-name-badge.search-highlight:hover {
        background-color: #ffecb3;
        color: #e65100;
    }

    /* Tooltip box – hidden by default */
    .doc-obs-tooltip {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        z-index: 9999;
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
        width: 240px;
        background: #1e293b;
        color: #f8fafc;
        border-radius: 10px;
        padding: 0.65rem 0.8rem;
        font-size: 0.72rem;
        line-height: 1.45;
        text-align: left;
        pointer-events: none;
        box-shadow: 0 10px 25px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.1);
        transition: opacity 0.18s ease, visibility 0.18s ease;
        white-space: normal;
        word-break: break-word;
    }
    
    /* Custom Search Bar */
    .custom-search-marker {
        display: none;
    }

    /* Fila de búsqueda sin recuadro de borde */
    div[data-testid="stHorizontalBlock"]:has(.search-label) {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 0.35rem 0rem !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 0.25rem !important;
        box-shadow: none !important;
    }
    
    /* Ocultar por completo el contenedor del marcador para que no ocupe espacio vertical */
    div[data-testid="stElementContainer"]:has(.columns-card-marker) {
        display: none !important;
        height: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Ocultar por completo contenedores de iframes con height 0 para eliminar espacio vertical vacío */
    div[data-testid="stElementContainer"]:has(iframe[height="0"]),
    div[data-testid="stElementContainer"]:has(iframe[style*="height: 0px"]),
    iframe[height="0"] {
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* Contenedor de columnas como una tarjeta interna premium (recuadro de la tabla de turnos) */
    div[data-testid="stVerticalBlock"]:has(.columns-card-marker) {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.35rem 1rem 1rem 1rem !important;
        margin-top: -0.65rem !important;
        margin-bottom: 0.75rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }
    
    /* ---- Calendar Grid: compactar elementos ---- */
    div[data-testid="stColumn"]:has(.saturday-col-marker) div[data-testid="stVerticalBlock"] {
        gap: 0.25rem !important;
    }
    div[data-testid="stColumn"]:has(.saturday-col-marker) button {
        min-height: unset !important;
        height: auto !important;
    }
    /* Resolver el margen negativo de Streamlit en Markdown que causa el solapamiento */
    div[data-testid="stColumn"]:has(.saturday-col-marker) div[data-testid="stMarkdownContainer"] {
        margin-bottom: 0px !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: stretch !important;
    }
    
    /* Resetear todos los contenedores intermedios de Streamlit en la fila de búsqueda */
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stMarkdownContainer"],
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Contenedor del Buscador (Estado por defecto con borde verde agua / menta suave) */
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"],
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]),
    /* Contenedor del Buscador (Estado por defecto con borde verde agua / menta suave) */
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"],
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]),
    div[data-testid="column"]:has(.custom-search-marker) div[data-testid="stTextInput"],
    div[data-testid="stColumn"]:has(.custom-search-marker) div[data-testid="stTextInput"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        max-width: 340px !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]) div[data-baseweb="input"],
    div[data-testid="column"]:has(.custom-search-marker) div[data-baseweb="input"],
    div[data-testid="stColumn"]:has(.custom-search-marker) div[data-baseweb="input"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-radius: 14px !important;
        border: 1.5px solid #5ec2ba !important;
        box-shadow: none !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 38px !important;
        width: 100% !important;
        max-width: 340px !important;
        margin: 0 auto !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        box-sizing: border-box !important;
    }
    
    /* Estado Hover del Buscador */
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"] div[data-baseweb="input"]:hover,
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]) div[data-baseweb="input"]:hover,
    div[data-testid="column"]:has(.custom-search-marker) div[data-baseweb="input"]:hover,
    div[data-testid="stColumn"]:has(.custom-search-marker) div[data-baseweb="input"]:hover {
        border-color: #0f9a9b !important;
    }
    
    /* Estado Focus / Activo del Buscador (Borde verde agua intenso + resplandor suave) */
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]) div[data-baseweb="input"]:focus-within,
    div[data-testid="column"]:has(.custom-search-marker) div[data-baseweb="input"]:focus-within,
    div[data-testid="stColumn"]:has(.custom-search-marker) div[data-baseweb="input"]:focus-within {
        border-color: #0f9a9b !important;
        box-shadow: 0 0 0 3px rgba(15, 154, 155, 0.18) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"] div[data-baseweb="input"] > div,
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]) div[data-baseweb="input"] > div,
    div[data-testid="column"]:has(.custom-search-marker) div[data-baseweb="input"] > div,
    div[data-testid="stColumn"]:has(.custom-search-marker) div[data-baseweb="input"] > div {
        background-color: transparent !important;
        border: none !important;
        border-radius: 14px !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Input interno con icono de lupa estilizado */
    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"] input,
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]) input,
    div[data-testid="column"]:has(.custom-search-marker) input,
    div[data-testid="stColumn"]:has(.custom-search-marker) input {
        height: 100% !important;
        min-height: 34px !important;
        max-height: 36px !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        background-color: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 14px !important;
        padding-left: 36px !important;
        padding-right: 12px !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%230f9a9b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16" y2="16"></line></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 11px center !important;
        background-size: 16px 16px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: #0f172a !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.search-label) div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextInput"]:has(input[aria-label="Buscador"]) input:focus,
    div[data-testid="column"]:has(.custom-search-marker) input:focus,
    div[data-testid="stColumn"]:has(.custom-search-marker) input:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.search-label) button {
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 8px !important;
    }
    
    .search-label {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        height: 32px;
        font-weight: 500;
        color: #7f8fa6;
        font-size: 0.88rem;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 32px !important;
    }
    
    .search-label p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 32px !important;
    }

    /* Buscador Centrado y Resaltado Reactivo en Vivo */
    div[data-testid="column"]:has(.custom-search-marker),
    div[data-testid="stColumn"]:has(.custom-search-marker) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }

    div[data-testid="column"]:has(.custom-search-marker) div[data-testid="stTextInput"],
    div[data-testid="stColumn"]:has(.custom-search-marker) div[data-testid="stTextInput"] {
        width: 100% !important;
        max-width: 340px !important;
        margin: 0 auto !important;
    }

    /* Ocultar cualquier texto placeholder en el buscador centrado */
    div[data-testid="column"]:has(.custom-search-marker) input::placeholder,
    div[data-testid="stColumn"]:has(.custom-search-marker) input::placeholder,
    input[aria-label="Buscador"]::placeholder {
        color: transparent !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }

    .search-highlight-active,
    .search-highlight-active *,
    .search-highlight-active p,
    .search-highlight-active span,
    .search-highlight-active div {
        text-decoration: underline !important;
        text-decoration-color: #0f9a9b !important;
        text-decoration-thickness: 3px !important;
        text-underline-offset: 4px !important;
        background-color: #ecfdf5 !important;
        box-shadow: 0 0 10px rgba(15, 154, 155, 0.35) !important;
        opacity: 1 !important;
        transition: all 0.15s ease !important;
    }

    .search-dimmed {
        opacity: 0.28 !important;
        filter: grayscale(40%) !important;
        transition: opacity 0.15s ease !important;
    }

    /* Estilos para los botones con fondo blanco por defecto y color en hover/active/focus */
    
    /* Ocultar marcadores de botones de búsqueda */
    div[data-testid="stElementContainer"]:has(.search-btn-marker),
    div[data-testid="stElementContainer"]:has(.clear-btn-marker),
    div[data-testid="stElementContainer"]:has(.refresh-btn-marker) {
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 1. Botón de Buscar (Degradado Azul) */
    div[data-testid="stColumn"]:has(.search-btn-marker) button {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #1b8dfd 0%, #0866ea 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 3px 10px rgba(8, 102, 234, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(.search-btn-marker) button p {
        font-size: 0 !important; /* Oculta la letra original B */
    }
    div[data-testid="stColumn"]:has(.search-btn-marker) button:hover,
    div[data-testid="stColumn"]:has(.search-btn-marker) button:focus {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #2896ff 0%, #075cd4 100%) !important;
        box-shadow: 0 4px 14px rgba(8, 102, 234, 0.45) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(.search-btn-marker) button:active {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #0e7ae6 0%, #054eb8 100%) !important;
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(8, 102, 234, 0.3) !important;
    }
    
    /* 2. Botón de Limpiar (Degradado Rojo) */
    div[data-testid="stColumn"]:has(.clear-btn-marker) button {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/><path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #ef4444 0%, #dc2626 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 3px 10px rgba(220, 38, 38, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(.clear-btn-marker) button p {
        font-size: 0 !important; /* Oculta la letra original L */
    }
    div[data-testid="stColumn"]:has(.clear-btn-marker) button:hover,
    div[data-testid="stColumn"]:has(.clear-btn-marker) button:focus {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/><path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #f87171 0%, #b91c1c 100%) !important;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.45) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(.clear-btn-marker) button:active {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/><path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #dc2626 0%, #991b1b 100%) !important;
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3) !important;
    }
    
    /* 3. Botón de Refrescar (Degradado Verde) */
    div[data-testid="stColumn"]:has(.refresh-btn-marker) button {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"/><path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #22c55e 0%, #15803d 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 3px 10px rgba(21, 128, 61, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(.refresh-btn-marker) button p {
        font-size: 0 !important; /* Oculta la letra original R */
    }
    div[data-testid="stColumn"]:has(.refresh-btn-marker) button:hover,
    div[data-testid="stColumn"]:has(.refresh-btn-marker) button:focus {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"/><path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #34d399 0%, #166534 100%) !important;
        box-shadow: 0 4px 14px rgba(21, 128, 61, 0.45) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(.refresh-btn-marker) button:active {
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%23ffffff"><path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"/><path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"/></svg>') center / 1rem no-repeat, linear-gradient(180deg, #15803d 0%, #14532d 100%) !important;
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(21, 128, 61, 0.3) !important;
    }

    /* Ocultar marcadores de botones de filtro */
    div[data-testid="stElementContainer"]:has(.filter-all-marker),
    div[data-testid="stElementContainer"]:has(.filter-normal-marker),
    div[data-testid="stElementContainer"]:has(.filter-comp-marker) {
        display: none !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 5. Botón de Filtro Todos (Degradado Azul) - Tamaño Compacto */
    div[data-testid="stColumn"]:has(.filter-all-marker) button,
    div[data-testid="column"]:has(.filter-all-marker) button {
        height: 28px !important;
        min-height: 28px !important;
        max-height: 28px !important;
        line-height: 26px !important;
        padding: 0 0.5rem !important;
        border-radius: 8px !important;
        max-width: 110px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="secondary"],
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="secondary"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1.5px solid #1b8dfd !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="secondary"] p,
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="secondary"] p {
        color: #0866ea !important;
        transition: color 0.2s ease !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 26px !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="secondary"]:hover,
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="secondary"]:hover {
        background: linear-gradient(180deg, #1b8dfd 0%, #0866ea 100%) !important;
        border-color: #0866ea !important;
        box-shadow: 0 4px 14px rgba(8, 102, 234, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="secondary"]:hover p,
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="secondary"]:hover p {
        color: #ffffff !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="primary"],
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="primary"] {
        background: linear-gradient(180deg, #1b8dfd 0%, #0866ea 100%) !important;
        background-color: #0866ea !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(8, 102, 234, 0.35) !important;
        transition: all 0.2s ease !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15) !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="primary"] p,
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="primary"] p {
        color: #ffffff !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 26px !important;
    }
    div[data-testid="stColumn"]:has(.filter-all-marker) button[data-testid*="primary"]:hover,
    div[data-testid="column"]:has(.filter-all-marker) button[data-testid*="primary"]:hover {
        background: linear-gradient(180deg, #2896ff 0%, #075cd4 100%) !important;
        box-shadow: 0 6px 18px rgba(8, 102, 234, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* 6. Botón de Filtro Normal (Degradado Verde) - Tamaño Compacto */
    div[data-testid="stColumn"]:has(.filter-normal-marker) button,
    div[data-testid="column"]:has(.filter-normal-marker) button {
        height: 28px !important;
        min-height: 28px !important;
        max-height: 28px !important;
        line-height: 26px !important;
        padding: 0 0.5rem !important;
        border-radius: 8px !important;
        max-width: 110px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="secondary"],
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="secondary"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1.5px solid #22c55e !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="secondary"] p,
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="secondary"] p {
        color: #15803d !important;
        transition: color 0.2s ease !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 26px !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="secondary"]:hover,
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="secondary"]:hover {
        background: linear-gradient(180deg, #22c55e 0%, #15803d 100%) !important;
        border-color: #15803d !important;
        box-shadow: 0 4px 14px rgba(21, 128, 61, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="secondary"]:hover p,
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="secondary"]:hover p {
        color: #ffffff !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="primary"],
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="primary"] {
        background: linear-gradient(180deg, #22c55e 0%, #15803d 100%) !important;
        background-color: #15803d !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(21, 128, 61, 0.35) !important;
        transition: all 0.2s ease !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15) !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="primary"] p,
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="primary"] p {
        color: #ffffff !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 26px !important;
    }
    div[data-testid="stColumn"]:has(.filter-normal-marker) button[data-testid*="primary"]:hover,
    div[data-testid="column"]:has(.filter-normal-marker) button[data-testid*="primary"]:hover {
        background: linear-gradient(180deg, #34d399 0%, #166534 100%) !important;
        box-shadow: 0 6px 18px rgba(21, 128, 61, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* 7. Botón de Filtro Compensación (Degradado Amarillo/Ámbar) - Tamaño Compacto */
    div[data-testid="stColumn"]:has(.filter-comp-marker) button,
    div[data-testid="column"]:has(.filter-comp-marker) button {
        height: 28px !important;
        min-height: 28px !important;
        max-height: 28px !important;
        line-height: 26px !important;
        padding: 0 0.5rem !important;
        border-radius: 8px !important;
        max-width: 135px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="secondary"],
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="secondary"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1.5px solid #f59e0b !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="secondary"] p,
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="secondary"] p {
        color: #b45309 !important;
        transition: color 0.2s ease !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 26px !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="secondary"]:hover,
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="secondary"]:hover {
        background: linear-gradient(180deg, #fbbf24 0%, #d97706 100%) !important;
        border-color: #d97706 !important;
        box-shadow: 0 4px 14px rgba(217, 119, 6, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="secondary"]:hover p,
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="secondary"]:hover p {
        color: #ffffff !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="primary"],
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="primary"] {
        background: linear-gradient(180deg, #fbbf24 0%, #d97706 100%) !important;
        background-color: #d97706 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35) !important;
        transition: all 0.2s ease !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15) !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="primary"] p,
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="primary"] p {
        color: #ffffff !important;
        margin: 0 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 26px !important;
    }
    div[data-testid="stColumn"]:has(.filter-comp-marker) button[data-testid*="primary"]:hover,
    div[data-testid="column"]:has(.filter-comp-marker) button[data-testid*="primary"]:hover {
        background: linear-gradient(180deg, #fcd34d 0%, #b45309 100%) !important;
        box-shadow: 0 6px 18px rgba(217, 119, 6, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* 4. Botón de Iniciar Sesión (Azul con texto) */
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"],
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"] {
        background-color: #ffffff !important;
        color: #1a73e8 !important;
        border: 1.5px solid #1a73e8 !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.1s ease !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"] p,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"] p {
        color: #1a73e8 !important;
        transition: color 0.2s ease !important;
        margin: 0 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"]:hover,
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"]:active,
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"]:focus,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"]:active,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"]:focus {
        background-color: #1a73e8 !important;
        border-color: #1a73e8 !important;
        color: #ffffff !important;
    }
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"]:hover p,
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"]:active p,
    div[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"]:focus p,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"]:hover p,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"]:active p,
    div[data-testid="stPopover"] button[data-testid="baseButton-secondary"]:focus p {
        color: #ffffff !important;
    }
    
    /* 8. Botón de Encabezado de Fecha (Degradado Azul Eléctrico Vibrante) */
    button.custom-header-btn,
    div[data-testid="stElementContainer"]:has(.date-header-marker) + div[data-testid="stElementContainer"] button {
        background: linear-gradient(180deg, #1b8dfd 0%, #0866ea 100%) !important;
        background-color: #0866ea !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(8, 102, 234, 0.35) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        line-height: 1.3 !important;
        padding: 0.6rem 0.6rem !important;
        width: 100% !important;
        display: block !important;
        margin-bottom: 0.75rem !important;
        border-radius: 12px !important;
        min-height: unset !important;
        height: auto !important;
        transition: all 0.2s ease !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15) !important;
    }
    button.custom-header-btn:hover,
    button.custom-header-btn:focus,
    div[data-testid="stElementContainer"]:has(.date-header-marker) + div[data-testid="stElementContainer"] button:hover,
    div[data-testid="stElementContainer"]:has(.date-header-marker) + div[data-testid="stElementContainer"] button:focus {
        background: linear-gradient(180deg, #2896ff 0%, #075cd4 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 6px 18px rgba(8, 102, 234, 0.5) !important;
        transform: translateY(-1px) !important;
    }
    button.custom-header-btn:active,
    div[data-testid="stElementContainer"]:has(.date-header-marker) + div[data-testid="stElementContainer"] button:active {
        background: linear-gradient(180deg, #0e7ae6 0%, #054eb8 100%) !important;
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(8, 102, 234, 0.3) !important;
    }
    button.custom-header-btn p, 
    button.custom-header-btn span, 
    button.custom-header-btn *,
    div[data-testid="stElementContainer"]:has(.date-header-marker) + div[data-testid="stElementContainer"] button * {
        color: #ffffff !important;
        background-color: transparent !important;
        font-weight: 700 !important;
    }

    /* 9. Botones de Médico en Modo Editor (Admin) - Fondo Blanco */
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="stBaseButton-secondary"]:not(.custom-header-btn),
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="baseButton-secondary"]:not(.custom-header-btn) {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #262730 !important;
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        padding: 0.22rem 0.5rem !important;
        line-height: 1.25 !important;
        text-shadow: none !important;
    }
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="stBaseButton-secondary"]:not(.custom-header-btn) *,
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="baseButton-secondary"]:not(.custom-header-btn) * {
        color: #262730 !important;
        background-color: transparent !important;
        font-weight: 500 !important;
        text-shadow: none !important;
    }
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="stBaseButton-secondary"]:not(.custom-header-btn):hover,
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="baseButton-secondary"]:not(.custom-header-btn):hover {
        background: #f1f5f9 !important;
        background-color: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        color: #1e293b !important;
        transform: scale(1.01) !important;
    }
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="stBaseButton-secondary"]:not(.custom-header-btn):hover *,
    div[data-testid="stColumn"]:has(.saturday-col-marker) button[data-testid="baseButton-secondary"]:not(.custom-header-btn):hover * {
        color: #1e293b !important;
    }
    



    /* Arrow pointer below the tooltip */
    .doc-obs-tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: #1e293b;
    }

    /* Show tooltip on badge hover */
    .doc-btn-wrap:hover .doc-obs-tooltip {
        visibility: visible;
        opacity: 1;
    }

    .shift-obs-title {
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 0.03em;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 0.2rem;
    }

    .shift-obs-item {
        display: flex;
        align-items: flex-start;
        gap: 0.35rem;
        margin-top: 0.3rem;
    }

    .shift-obs-icon {
        color: #93c5fd;
        margin-top: 2px;
        flex-shrink: 0;
        font-size: 0.75rem;
    }
    
    /* Timeline styling */
    .timeline-item {
        border-left: 2px solid #1976d2;
        padding-left: 1.5rem;
        position: relative;
        padding-bottom: 1.5rem;
    }
    
    .timeline-item::after {
        content: '';
        position: absolute;
        left: -6px;
        top: 4px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #1976d2;
        border: 2px solid white;
    }
    
    .timeline-date {
        font-size: 0.85rem;
        font-weight: 700;
        color: #0d47a1;
        margin-bottom: 0.15rem;
    }
    
    .timeline-content {
        font-size: 0.9rem;
        color: #455a64;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .status-pendiente {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    
    .status-aprobado {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-rechazado {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* Supernumerary profile cards */
    .doc-profile-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .doc-profile-name {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
    }
    
    .doc-profile-meta {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        padding: 0.8rem 0;
        color: #90a4ae;
        font-size: 0.8rem;
        margin-top: 1rem;
    }

    /* Eliminar borde inferior del último bloque antes del footer */
    section.main > div:last-child {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stMainBlockContainer > div > div > div:last-child {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    
    /* Custom style for Streamlit standard components */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(240, 244, 248, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.03);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        background-color: transparent;
        color: #546e7a;
        font-weight: 500;
        transition: all 0.2s;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255,255,255,0.7);
        color: #1976d2;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #1976d2 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        font-weight: 700 !important;
    }
    
    /* Adjust Streamlit main container padding */
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer,
    .block-container {
        padding-top: 0px !important;
        padding-left: 0px !important;
        padding-right: 0px !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Header styling in normal page flow */
    div[data-testid="stHorizontalBlock"]:has(.main-title) {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%) !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        border-radius: 16px !important;
        padding: 1rem 1.5rem !important;
        margin-top: 0px !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
        display: flex !important;
        align-items: center !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.main-title) div[data-testid="stColumn"] {
        display: flex !important;
        align-items: center !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.main-title) div[data-testid="stColumn"]:first-of-type {
        justify-content: center !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.main-title) div[data-testid="stColumn"]:last-of-type {
        justify-content: flex-start !important;
        padding-left: 0.75rem !important;
    }
    
    /* Make default Streamlit header completely hidden to remove Share/GitHub/Menu icons */
    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide Manage App button (viewer badge in bottom right corner) */
    .viewerBadge_container, 
    [data-testid="viewerBadge"],
    .stAppDeployButton,
    div[class^="viewerBadge_container"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Adjust Main Title inside header */
    .main-title {
        font-family: 'Outfit', sans-serif !important;
        background: linear-gradient(135deg, #0d47a1 0%, #1976d2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    
    /* Adjust tabs container to push content below the header */
    .stTabs {
        margin-top: 0px !important;
    }
    
    /* Ocultar contenedores de marcadores */
    div[data-testid="stElementContainer"]:has(.admin-gear-marker),
    div[data-testid="stElementContainer"]:has(.topbar-user-marker) {
        display: none !important;
        height: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Botón de usuario en el topbar institucional (Píldora con avatar de iniciales JJ) */
    div[data-testid="column"]:has(.topbar-user-marker),
    div[data-testid="stColumn"]:has(.topbar-user-marker) {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"],
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button[data-testid="stPopoverButton"],
    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button[data-testid="stPopoverButton"],
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 8px !important;
        padding: 0.25rem 0.65rem !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.45rem !important;
        cursor: pointer !important;
        width: auto !important;
        min-width: auto !important;
        height: 34px !important;
        min-height: 34px !important;
        margin-top: 5px !important;
        margin-bottom: 0 !important;
        margin-left: 12px !important;
        margin-right: 0 !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover {
        background-color: rgba(0, 0, 0, 0.04) !important;
        border: none !important;
        box-shadow: none !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:focus,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Icono de persona bi-person antes del texto */
    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button::before,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button::before {
        content: "\\f4da" !important;
        font-family: 'bootstrap-icons' !important;
        font-style: normal !important;
        font-weight: normal !important;
        font-size: 1.25rem !important;
        color: #0284c7 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        background: transparent !important;
        border-radius: 0 !important;
        width: auto !important;
        height: auto !important;
        transition: color 0.15s ease !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover::before,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover::before {
        color: #0369a1 !important;
    }

    /* Texto Conexion operativa al lado del icono de persona */
    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button p,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button p {
        display: inline-flex !important;
        align-items: center !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
        transition: color 0.15s ease !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover p,
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover p {
        color: #0284c7 !important;
    }

    /* Flecha chevron hacia abajo al lado del texto */
    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button div[aria-hidden="true"],
    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button [data-testid="stIconMaterial"],
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button div[aria-hidden="true"],
    div[data-testid="stColumn"]:has(.topbar-user-marker) div[data-testid="stPopover"] button [data-testid="stIconMaterial"] {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #64748b !important;
        font-size: 1.15rem !important;
        margin-left: 0.2rem !important;
        line-height: 1 !important;
        transition: color 0.15s ease !important;
    }

    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover div[aria-hidden="true"],
    div[data-testid="column"]:has(.topbar-user-marker) div[data-testid="stPopover"] button:hover [data-testid="stIconMaterial"] {
        color: #0284c7 !important;
    }

    /* Estilos del botón de engranaje administrativo en el Popover (fallback) */
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button {
        background-color: #ffffff !important;
        border: 2px solid #d9d9d9 !important;
        border-radius: 50% !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
        padding: 0 !important;
        transition: all 0.2s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 38px !important;
        width: 38px !important;
        min-height: 38px !important;
        min-width: 38px !important;
        cursor: pointer !important;
    }
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button:hover,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button:hover {
        background-color: #f1f5f9 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18) !important;
        border-color: #0284c7 !important;
    }
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button p,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button p {
        font-size: 1.25rem !important;
        color: #3f3e3e !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        visibility: visible !important;
    }
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button:hover p,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button:hover p {
        color: #0284c7 !important;
    }
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button div[aria-hidden="true"],
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button [data-testid="stIconMaterial"],
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button svg,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button div[aria-hidden="true"],
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button [data-testid="stIconMaterial"],
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button svg {
        display: none !important;
    }
    
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button div,
    div[data-testid="column"]:has(.admin-gear-marker) div[data-testid="stPopover"] button span,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button div,
    div[data-testid="stColumn"]:has(.admin-gear-marker) div[data-testid="stPopover"] button span {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0px !important;
        padding: 0px !important;
        height: 100% !important;
        width: 100% !important;
    }
    
    /* Añadir icono bi-arrow-clockwise al botón Refrescar */
    div[data-testid="stElementContainer"]:has(.refresh-btn-wrapper) + div[data-testid="stElementContainer"] button p::before,
    div.element-container:has(.refresh-btn-wrapper) + div.element-container button p::before {
        content: "\\f130"; /* bi-arrow-clockwise */
        font-family: "bootstrap-icons";
        margin-right: 0.5rem;
        font-size: 1.15rem;
        vertical-align: middle;
        font-weight: 800;
        color: #0d47a1;
        transition: transform 0.3s ease;
        display: inline-block;
    }
    
    div[data-testid="stElementContainer"]:has(.refresh-btn-wrapper) + div[data-testid="stElementContainer"] button:hover p::before,
    div.element-container:has(.refresh-btn-wrapper) + div.element-container button:hover p::before {
        transform: rotate(180deg);
    }
    
    /* Añadir icono bi-plus-square al botón Agregar Médico */
    div[data-testid="stElementContainer"]:has(.add-doc-btn-wrapper) + div[data-testid="stElementContainer"] button p::before,
    div.element-container:has(.add-doc-btn-wrapper) + div.element-container button p::before {
        content: "\\f4fb"; /* bi-plus-square */
        font-family: "bootstrap-icons";
        margin-right: 0.4rem;
        font-size: 1.3rem;
        vertical-align: middle;
        font-weight: 800;
        color: #7e57c2; /* Color morado similar al emoji original */
        display: inline-block;
    }
    
    /* Ocultar los contenedores inyectados para que no afecten el layout y alineación */
    div[data-testid="stElementContainer"]:has(.change-btn-wrapper),
    div.element-container:has(.change-btn-wrapper),
    div[data-testid="stElementContainer"]:has(.add-doc-btn-wrapper),
    div.element-container:has(.add-doc-btn-wrapper) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Añadir icono bi-arrow-clockwise al botón Cambiar / Reemplazar */
    div[data-testid="stElementContainer"]:has(.change-btn-wrapper) + div[data-testid="stElementContainer"] button p::before,
    div.element-container:has(.change-btn-wrapper) + div.element-container button p::before {
        content: "\\f130"; /* bi-arrow-clockwise */
        font-family: "bootstrap-icons";
        margin-right: 0.4rem;
        font-size: 1.15rem;
        vertical-align: middle;
        font-weight: 800;
        color: #0d47a1;
        transition: transform 0.3s ease;
        display: inline-block;
    }
    
    div[data-testid="stElementContainer"]:has(.change-btn-wrapper) + div[data-testid="stElementContainer"] button:hover p::before,
    div.element-container:has(.change-btn-wrapper) + div.element-container button:hover p::before {
        transform: rotate(180deg);
    }
    
    /* Añadir icono SVG personalizado de calendario a las pestañas en el centro de gestión */
    div[data-testid="stExpander"] .stTabs [data-baseweb="tab"]::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 6px;
        background-color: currentColor;
        -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5M1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z'/%3E%3C/svg%3E");
        mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5M1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4z'/%3E%3C/svg%3E");
        -webkit-mask-repeat: no-repeat;
        mask-repeat: no-repeat;
        -webkit-mask-size: contain;
        mask-size: contain;
        vertical-align: middle;
    }
    
    /* Añadir icono bi-clipboard-plus al botón Duplicar Programación */
    div[data-testid="stElementContainer"]:has(.dup-btn-wrapper) + div[data-testid="stElementContainer"] button p::before,
    div.element-container:has(.dup-btn-wrapper) + div.element-container button p::before {
        content: "\\f28e"; /* bi-clipboard-plus */
        font-family: "bootstrap-icons";
        margin-right: 0.4rem;
        font-size: 1.15rem;
        vertical-align: middle;
        font-weight: 800;
        color: #1e293b;
        display: inline-block;
    }
    
    /* Ocultar el contenedor inyectado de dup-btn-wrapper */
    div[data-testid="stElementContainer"]:has(.dup-btn-wrapper),
    div.element-container:has(.dup-btn-wrapper) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Estilo premium para botones primarios (Lighter Red) */
    button[data-testid="stBaseButton-primary"],
    button[data-testid="baseButton-primary"] {
        background-color: #ef5350 !important; /* Lighter/soft red */
        border-color: #ef5350 !important;
        color: #ffffff !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="stBaseButton-primary"]:hover,
    button[data-testid="stBaseButton-primary"]:active,
    button[data-testid="stBaseButton-primary"]:focus,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-primary"]:active,
    button[data-testid="baseButton-primary"]:focus {
        background-color: #e53935 !important; /* Slightly darker on hover */
        border-color: #e53935 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(239, 83, 80, 0.3) !important;
    }
    button[data-testid="stBaseButton-primary"] p,
    button[data-testid="stBaseButton-primary"] span,
    button[data-testid="stBaseButton-primary"] svg,
    button[data-testid="baseButton-primary"] p,
    button[data-testid="baseButton-primary"] span,
    button[data-testid="baseButton-primary"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    /* Bloqueo y eliminación del botón X de los diálogos para impedir cierres */
    button[aria-label="Close"],
    button[aria-label="Cerrar"],
    button[title="Close"],
    button[title="Cerrar"],
    div[data-testid="stDialog"] button[aria-label="Close"],
    div[data-testid="stDialog"] button[aria-label="Cerrar"],
    div[data-testid="stDialog"] button,
    div[role="dialog"] button[aria-label="Close"],
    div[role="dialog"] header + button,
    button[kind="header-close"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Regla especifica para mantener visibles solo los botones del formulario interno */
    div[data-testid="stDialog"] div[data-testid="stButton"] button,
    div[role="dialog"] div[data-testid="stButton"] button {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    
    div[data-testid="stModalBackdrop"],
    div[data-baseweb="modal-backdrop"] {
        pointer-events: none !important;
    }
    
    div[data-testid="stDialog"],
    div[role="dialog"],
    div[data-baseweb="modal"] {
        pointer-events: auto !important;
    }

    /* ========================================================= */
    /* COLOR PERSONALIZADO RGB(20, 116, 220) PARA BOTONES CLAVE */
    /* ========================================================= */
    button[data-testid="baseButton-primary"],
    button[kind="primary"] {
        background-color: rgb(20, 116, 220) !important;
        background: rgb(20, 116, 220) !important;
        border-color: rgb(20, 116, 220) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    button[data-testid="baseButton-primary"] *,
    button[kind="primary"] * {
        color: #ffffff !important;
    }

    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background-color: rgb(15, 95, 185) !important;
        background: rgb(15, 95, 185) !important;
        border-color: rgb(15, 95, 185) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(20, 116, 220, 0.35) !important;
    }

    button[data-testid="baseButton-primary"]:active,
    button[kind="primary"]:active {
        background-color: rgb(12, 75, 145) !important;
        background: rgb(12, 75, 145) !important;
        border-color: rgb(12, 75, 145) !important;
        color: #ffffff !important;
    }
    </style>
    """)
    clean_css = " ".join([line.strip() for line in css_content.split("\n") if line.strip()])
    st.markdown(clean_css, unsafe_allow_html=True)
