import sys

import streamlit as st
from config.paths import get_streamlit_app_dir


UI_DIR = get_streamlit_app_dir()
PAGES_DIR = UI_DIR / "pages"

if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

st.set_page_config(layout="wide")

pages = [
    st.Page(str(PAGES_DIR / "Upload_and_Run.py"), title="Upload Data & Run Model", icon="📤"),
    st.Page(str(PAGES_DIR / "Insights_and_Analysis.py"), title="Insights & Analysis", icon="🔍"),
]

pg = st.navigation(pages, position="top")
pg.run()

st.sidebar.markdown("## OpenBCA Resources")
st.sidebar.markdown("#### [Background](http://www.nationalenergyscreeningproject.org/open-source-bca-tool/)")
st.sidebar.markdown("#### [National Standard Practice Manual](http://www.nationalenergyscreeningproject.org/national-standard-practice-manual/)")
st.sidebar.markdown("#### [Open Source GitHub Repository](https://github.com/openbca/openbca)")