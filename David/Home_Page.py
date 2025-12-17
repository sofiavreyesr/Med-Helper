import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta
import re

DB_PATH = "med_helper.db"

st.set_page_config(
    page_title="Med Helper",
    page_icon="🩺",
    layout="wide"
)

# =========================
# CSS (FINAL + AESTHETIC)
# =========================
st.markdown("""
<style>

/* ---------- Theme variables ---------- */
:root{
  --blue-50:#eff6ff;
  --blue-100:#dbeafe;
  --blue-200:#bfdbfe;
  --blue-500:#3b82f6;
  --blue-600:#2563eb;
  --blue-700:#1d4ed8;
  --ink:#0f172a;
  --muted:#475569;
  --card:#ffffff;
  --border: rgba(37,99,235,0.18);
  --shadow: 0 10px 25px rgba(2,8,23,0.08);
  color-scheme: light;
}

/* ---------- App background ---------- */
.stApp{
  background:
    radial-gradient(1200px 600px at 10% 0%, var(--blue-50) 0%, #ffffff 55%),
    radial-gradient(900px 500px at 90% 15%, var(--blue-100) 0%, #ffffff 45%);
  color: var(--ink) !important;
}

/* ---------- Text safety ---------- */
.stApp, .stMarkdown, p, span, label, li{
  color: var(--ink) !important;
}

/* ---------- Streamlit top bar (keep it visible + light) ---------- */
header[data-testid="stHeader"]{
  background: #ffffff !important;
  border-bottom: 1px solid var(--border);
}
div[data-testid="stToolbar"]{
  background: transparent !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, #ffffff 0%, var(--blue-50) 100%) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] *{
  color: var(--ink) !important;
}

/* ---------- Header card ---------- */
.mh-header{
  padding: 18px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--blue-600), var(--blue-500));
  color: white;
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}
.mh-header h1{
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  color: white !important;
}
.mh-header p{
  margin-top: 6px;
  font-size: 14px;
  color: white !important;
}

/* ---------- Cards ---------- */
.mh-card{
  background: white !important;
  border-radius: 18px;
  border: 1px solid var(--border);
  padding: 16px;
  box-shadow: 0 6px 18px rgba(2,8,23,0.06);
}

/* ---------- Pills ---------- */
.pill{
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--blue-50);
  border: 1px solid var(--blue-200);
  color: var(--blue-700);
  font-weight: 700;
  font-size: 12px;
  margin-right: 6px;
}

/* ---------- Inputs ---------- */
input, textarea{
  background: white !important;
  color: var(--ink) !important;
  border-radius: 12px !important;
}

/* ---------- Inline code (sidebar tips) ---------- */
code{
  background: #eef2ff !important;
  color: var(--ink) !important;
  border: 1px solid var(--blue-200);
  border-radius: 8px;
  padding: 0.15rem 0.35rem;
}

/* ---------- Buttons (ALL) ---------- */
.stButton > button,
.stButton > button *{
  background: linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
  color: #ffffff !important;
  fill: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  border-radius: 12px !important;
  border: 1px solid rgba(37,99,235,0.25) !important;
  font-weight: 800 !important;
}

/* ---------- Form submit button ---------- */
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stFormSubmitButton"] > button *{
  background: linear-gradient(135deg, var(--blue-600), var(--blue-500)) !important;
  color: #ffffff !important;
  fill: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  border-radius: 12px !important;
  font-weight: 800 !important;
}

/* ---------- Date picker (calendar popup) ---------- */
div[data-baseweb="popover"],
div[data-baseweb="calendar"],
div[data-baseweb="calendar"] *{
  background: #ffffff !important;
  color: var(--ink) !important;
}
div[data-baseweb="calendar"] svg{
  fill: var(--ink) !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="mh-header">
  <h1>🩺 Med Helper</h1>
  <p>Deadlines + checklist + Anki card drafts (fast, practical, no fluff)</p>
</div>
""", unsafe_allow_html=True)

# =========================
# DB
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            due_date TEXT,
            tag TEXT,
            priority TEXT,
            done INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_task(title, due, tag, priority):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks VALUES (NULL,?,?,?,?,0,?)",
        (title, due, tag, priority, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM tasks", conn)
    conn.close()
    if not df.empty:
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date
    return df

init_db()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Deadlines & Tasks", "Anki Helper"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("""
- Keep tasks short (action verbs)
- One idea per line for Anki
- Tags like `Block1`, `Cardio`, `Anatomy`
""")

# =========================
# PAGES
# =========================
tasks = get_tasks()
today = date.today()

if page == "Anki Helper":
    st.markdown("<div class='mh-card'>", unsafe_allow_html=True)
    st.markdown("### 🧠 Anki Helper")
    raw = st.text_area("Notes / objectives", height=200)
    if st.button("✨ Generate cards"):
        st.success("Cards generated (placeholder)")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Deadlines & Tasks":
    st.markdown("<div class='mh-card'>", unsafe_allow_html=True)
    with st.form("add_task"):
        title = st.text_input("Task")
        due = st.date_input("Due date", value=None)
        tag = st.text_input("Tag")
        priority = st.selectbox("Priority", ["Low","Medium","High"])
        if st.form_submit_button("Add task"):
            add_task(title, due.isoformat() if due else None, tag, priority)
            st.success("Task added")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='mh-card'>", unsafe_allow_html=True)
    st.markdown("### Dashboard")
    st.write("Open:", len(tasks[tasks["done"]==0]) if not tasks.empty else 0)
    st.markdown("</div>", unsafe_allow_html=True)
