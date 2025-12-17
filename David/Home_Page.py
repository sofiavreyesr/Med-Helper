import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import re

DB_PATH = "med_helper.db"

st.set_page_config(page_title="Med Helper", page_icon="🩺", layout="wide")

# =========================
# CSS: Dark-Chrome-proof + Top bar visible + Fix black submit button
# =========================
st.markdown(
    """
    <style>
      :root{
        --blue-50:#eff6ff;
        --blue-100:#dbeafe;
        --blue-200:#bfdbfe;
        --blue-300:#93c5fd;
        --blue-500:#3b82f6;
        --blue-600:#2563eb;
        --blue-700:#1d4ed8;

        --ink:#0f172a;
        --muted:#475569;

        --card:#ffffff;
        --border: rgba(37, 99, 235, 0.18);
        --shadow: 0 10px 25px rgba(2, 8, 23, 0.08);

        /* Prevent Chrome forced-dark weirdness */
        color-scheme: light;
      }

      html{
        -webkit-text-size-adjust: 100%;
        forced-color-adjust: none;
      }

      /* ==========================
         STREAMLIT TOP BAR (VISIBLE + LIGHT)
         ========================== */
      header[data-testid="stHeader"]{
        background: rgba(255,255,255,0.92) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(37,99,235,0.18) !important;
      }
      div[data-testid="stToolbar"]{
        background: transparent !important;
      }
      header[data-testid="stHeader"] svg,
      div[data-testid="stToolbar"] svg{
        fill: var(--ink) !important;
        color: var(--ink) !important;
      }
      header[data-testid="stHeader"] button,
      div[data-testid="stToolbar"] button{
        background: transparent !important;
      }
      div[data-testid="stDecoration"]{
        background: transparent !important;
      }

      /* App background */
      .stApp{
        background:
          radial-gradient(1200px 600px at 10% 0%, var(--blue-50) 0%, #ffffff 55%),
          radial-gradient(900px 500px at 90% 15%, var(--blue-100) 0%, #ffffff 45%);
        color: var(--ink) !important;
      }

      /* Keep text readable everywhere */
      .stApp, .stMarkdown, label, p, span, div, li{
        color: var(--ink) !important;
      }

      /* Header card */
      .mh-header{
        padding: 18px 18px 14px 18px;
        border: 1px solid var(--border);
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500));
        color: #fff;
        border-radius: 18px;
        box-shadow: var(--shadow);
        margin-bottom: 14px;
      }
      .mh-header h1{
        font-size: 28px;
        line-height: 1.15;
        margin: 0;
        font-weight: 800;
        letter-spacing: 0.2px;
        color: #fff !important;
      }
      .mh-header p{
        margin: 6px 0 0 0;
        opacity: 0.92;
        font-size: 14px;
        color: #fff !important;
      }

      /* Cards */
      .mh-card{
        border: 1px solid var(--border);
        background: var(--card) !important;
        border-radius: 18px;
        padding: 16px 16px 14px 16px;
        box-shadow: 0 6px 18px rgba(2, 8, 23, 0.06);
      }
      .mh-card h3{
        margin: 0 0 10px 0;
        color: var(--ink) !important;
        font-size: 16px;
        font-weight: 800;
      }
      .mh-meta{
        color: var(--muted) !important;
        font-size: 13px;
        margin-top: 6px;
      }

      /* Pills */
      .pill{
        display:inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: var(--blue-50) !important;
        border: 1px solid var(--blue-200);
        color: var(--blue-700) !important;
        font-weight: 700;
        font-size: 12px;
        margin-right: 6px;
      }

      /* Sidebar */
      section[data-testid="stSidebar"]{
        background: linear-gradient(180deg, #ffffff 0%, var(--blue-50) 100%) !important;
        border-right: 1px solid var(--border);
      }
      section[data-testid="stSidebar"] *{
        color: var(--ink) !important;
      }

      /* Buttons */
      .stButton>button{
        border-radius: 12px !important;
        border: 1px solid rgba(37,99,235,0.25) !important;
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
      }
      .stButton>button:hover{
        filter: brightness(0.98);
        border-color: rgba(37,99,235,0.38);
      }

      /* ✅ FORCE all Streamlit buttons (including Generate cards) to have white text */
      .stButton > button,
      .stButton > button *{
        color: #ffffff !important;
        fill: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
      }

      /* ✅ FIX: Form submit button (was black block) */
      div[data-testid="stFormSubmitButton"] > button{
        border-radius: 12px !important;
        border: 1px solid rgba(37,99,235,0.25) !important;
        background: linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
      }
      div[data-testid="stFormSubmitButton"] > button *{
        color: #ffffff !important;
        fill: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
      }
      div[data-testid="stFormSubmitButton"] > button:hover{
        filter: brightness(0.98) !important;
        border-color: rgba(37,99,235,0.38) !important;
      }

      /* Download button */
      .stDownloadButton>button{
        border-radius: 12px !important;
        border: 1px solid rgba(37,99,235,0.25) !important;
        background: linear-gradient(135deg, #0ea5e9, var(--blue-500)) !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
      }

      /* Inputs (force light bg + dark text) */
      input, textarea{
        background-color: #ffffff !important;
        color: var(--ink) !important;
        caret-color: var(--ink);
        border-radius: 12px !important;
      }
      .stDateInput input{
        background-color: #ffffff !important;
        color: var(--ink) !important;
        border-radius: 12px !important;
      }

      /* Placeholders */
      ::placeholder{
        color: #64748b !important;
        opacity: 1;
      }

      /* KPI */
      .kpi{
        display:flex;
        gap: 12px;
      }
      .kpi .box{
        flex: 1;
        border: 1px solid var(--border);
        background: #fff !important;
        border-radius: 18px;
        padding: 14px 14px;
        box-shadow: 0 6px 18px rgba(2, 8, 23, 0.06);
      }
      .kpi .label{
        color: var(--muted) !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
      }
      .kpi .value{
        margin-top: 6px;
        color: var(--ink) !important;
        font-size: 22px;
        font-weight: 900;
      }

      /* Dataframe */
      div[data-testid="stDataFrame"]{
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid var(--border);
      }
      div[data-testid="stDataFrame"] *{
        color: var(--ink) !important;
        background-color: #ffffff !important;
      }

      /* Selectbox + listbox */
      div[data-baseweb="select"] > div{
        background: #ffffff !important;
        border: 1px solid rgba(15, 23, 42, 0.25) !important;
        border-radius: 12px !important;
      }
      div[data-baseweb="select"] span{ color: var(--ink) !important; }
      div[data-baseweb="select"] svg{ color: var(--ink) !important; fill: var(--ink) !important; }

      ul[role="listbox"]{
        background: #ffffff !important;
        color: var(--ink) !important;
        border: 1px solid rgba(15, 23, 42, 0.18) !important;
        border-radius: 12px !important;
      }
      ul[role="listbox"] li{
        background: #ffffff !important;
        color: var(--ink) !important;
      }

      /* Inline code pills */
      section[data]()
