'''
# Harper's Safeway Home Legal Triage & Output Suite
# Court File No.: FDSJ-739-2024

**Main Dashboard**
'''

import streamlit as st

st.set_page_config(
    page_title="Harper's Safeway Home - Legal Suite",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main_dashboard():
    st.title("⚖️ Harper's Safeway Home Legal Triage & Output Suite")
    st.sidebar.success("Main Dashboard")

    # Display Case Overview
    st.header("Case Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Exhibits", "11,619+")
    col2.metric("Date Range", "Aug 2024 - Jun 2025")
    col3.metric("Filing Deadline", "November 4, 2025")

if __name__ == '__main__':
    main_dashboard()
