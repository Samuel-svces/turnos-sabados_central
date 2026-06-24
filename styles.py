# Styles and Custom CSS for TURNOS SABADOS Application

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
    
    /* Global Styles */
    html, body, .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hide the Streamlit top header (hamburger menu) to save space */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
    }
    
    /* Reduce top padding to remove empty space above banner */
    .block-container, div[data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        margin-top: -1rem !important;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    /* App Background Gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(90, 92, 106, 0.03) 0%, rgba(32, 45, 58, 0.05) 90%);
    }
    
    /* Full width header banner */
    .header-banner-marker {
        display: none;
    }
    div[data-testid="stHorizontalBlock"]:has(.premium-banner-transparent) {
        background: linear-gradient(to right, #1a2238 0%, #3a506b 60%, #b2ccd6 100%);
        border-radius: 12px;
        padding: 8px 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        align-items: center;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.premium-banner-transparent) > div[data-testid="column"] {
        /* Centrar contenido verticalmente y quitar márgenes extra */
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Transparent container for title text inside banner */
    .premium-banner-transparent {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        padding-left: 10px;
    }
    
    /* Style the popover button (gear) to be white */
    div[data-testid="stHorizontalBlock"]:has(.premium-banner-transparent) div[data-testid="stPopover"] button {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.premium-banner-transparent) div[data-testid="stPopover"] button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.premium-banner-transparent) div[data-testid="stPopover"] button p {
        filter: brightness(0) invert(1);
    }
    .premium-banner-icon {
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        flex-shrink: 0;
    }
    .premium-banner-icon i {
        color: white;
        font-size: 1.3rem;
    }
    .premium-banner-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .premium-banner-text h1 {
        color: white !important;
        font-size: 1.4rem !important;
        margin: 0 !important;
        padding: 0 !important;
        font-weight: 700 !important;
        letter-spacing: 0px !important;
        line-height: 1.2 !important;
        -webkit-text-fill-color: white !important;
    }
    .premium-banner-text p {
        color: rgba(255, 255, 255, 0.85) !important;
        margin: 0 !important;
        padding: 0 !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
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
        margin-top: 1rem;
    }
    
    .saturday-col {
        background: #f0f4ff;
        border: 1px solid #c2dcf6;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(13, 71, 161, 0.02);
        display: flex;
        flex-direction: column;
        height: 100%;
        transition: border-color 0.2s;
    }
    
    .saturday-col:hover {
        border-color: #0d47a1;
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
        margin-bottom: 0.4rem;
    }

    /* The clickable name badge */
    .doc-name-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        width: 100%;
        box-sizing: border-box;
        padding: 0.38rem 0.65rem;
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
    .custom-search-marker + div[data-testid="stTextInput"] input {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="%232b8a8b"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/></svg>');
        background-repeat: no-repeat;
        background-position: 12px center;
        background-size: 18px;
        padding-left: 38px !important;
        border-radius: 12px !important;
        border: 1px solid #d1e5e5 !important;
        color: #2b8a8b !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .custom-search-marker + div[data-testid="stTextInput"] input:focus {
        border-color: #2b8a8b !important;
        box-shadow: 0 0 0 1px #2b8a8b !important;
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
        padding: 2rem 0;
        color: #90a4ae;
        font-size: 0.8rem;
        border-top: 1px solid rgba(0,0,0,0.05);
        margin-top: 4rem;
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
    
    /* Adjust Streamlit main container padding to pull page contents up */
    [data-testid="stMainBlockContainer"] {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
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
    
    /* Reemplazar emoji de engranaje por icono bi-gear de Bootstrap en el Popover */
    div[data-testid="stPopover"] button p {
        font-size: 0; /* Oculta el emoji original */
    }
    div[data-testid="stPopover"] button p::before {
        content: "\\f3e5"; /* bi-gear */
        font-family: "bootstrap-icons";
        font-size: 1.4rem;
        color: #546e7a;
        visibility: visible;
        display: inline-block;
        line-height: 1;
    }
    div[data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    div[data-testid="stPopover"] button:hover {
        color: #1976d2 !important;
    }
    div[data-testid="stPopover"] button:hover p::before {
        color: #1976d2;
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
    </style>
    """)
    clean_css = " ".join([line.strip() for line in css_content.split("\n") if line.strip()])
    st.markdown(clean_css, unsafe_allow_html=True)
