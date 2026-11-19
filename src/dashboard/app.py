"""Streamlit entry point.

    streamlit run src/dashboard/app.py

The page scripts live in <repo>/pages, which Streamlit does not auto-discover
(it only looks next to this file), so they are registered explicitly.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # lets the pages import `src.*`

import streamlit as st  # noqa: E402

st.set_page_config(

    page_title="Nifty 100 Analytics",

    layout="wide",

    initial_sidebar_state="expanded"

)

PAGES = [
    ("01_home.py", "Home", "🏠"),
    ("02_profile.py", "Company Profile", "🏢"),
    ("03_screener.py", "Screener", "🔎"),
    ("04_peers.py", "Peers", "👥"),
    ("05_trends.py", "Trends", "📈"),
    ("06_sectors.py", "Sectors", "🏭"),
    ("07_capital.py", "Capital Allocation", "💰"),
    ("08_reports.py", "Annual Reports", "📄"),
]

nav = st.navigation([
    st.Page(ROOT / "pages" / file, title=title, icon=icon, default=(i == 0))
    for i, (file, title, icon) in enumerate(PAGES)
])

nav.run()
