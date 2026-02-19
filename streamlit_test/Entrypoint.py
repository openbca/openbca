import streamlit as st

st.set_page_config(layout="wide")

pages = [
    st.Page("pages/Upload_and_Run.py", title="Upload Data & Run Model", icon="📤"),
    st.Page("pages/Insights_and_Analysis.py", title="Insights & Analysis", icon="🔍"),
]

pg = st.navigation(pages, position="top")
pg.run()

st.sidebar.markdown("## OpenBCA Resources")
st.sidebar.markdown("#### [Background](http://www.nationalenergyscreeningproject.org/open-source-bca-tool/)")
st.sidebar.markdown("#### [National Standard Practice Manual](http://www.nationalenergyscreeningproject.org/national-standard-practice-manual/)")
st.sidebar.markdown("#### [Open Source GitHub Repository](https://github.com/openbca/openbca)")
