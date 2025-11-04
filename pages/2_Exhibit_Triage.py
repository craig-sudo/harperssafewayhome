
import streamlit as st
import pandas as pd
from utils import load_exhibit_data # Import from the new utils file

st.set_page_config(
    page_title="Exhibit Triage - Legal Suite",
    page_icon="🗂️",
    layout="wide"
)

st.title("🗂️ Exhibit Triage & Selection")
st.write("Use the filters below to review, sort, and select exhibits for the final package. The table is fully interactive.")

df = load_exhibit_data()

if df.empty:
    st.error("Error: CUSTODY_COURT_EXHIBITS.txt not found. Please ensure the file is in the root directory.")
else:
    st.info(f"Successfully loaded and parsed **{len(df):,}** unique exhibits.")

    # --- Filtering UI ---
    st.write("### Filters")
    left, middle, right = st.columns(3)

    # Category Filter
    categories = ["All"] + sorted(df['Category'].unique().tolist())
    selected_category = left.selectbox("Filter by Category", options=categories)

    # Text Search Filter
    search_term = middle.text_input("Search in Context")

    # Score Filter
    min_score, max_score = right.slider(
        "Filter by Score",
        min_value=float(df['Score'].min()),
        max_value=float(df['Score'].max()),
        value=(float(df['Score'].min()), float(df['Score'].max()))
    )

    # --- Apply Filters ---
    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['Context'].str.contains(search_term, case=False, na=False)]

    filtered_df = filtered_df[(filtered_df['Score'] >= min_score) & (filtered_df['Score'] <= max_score)]

    st.write("---")

    # --- Display DataFrame ---
    st.write(f"### Displaying {len(filtered_df):,} Exhibits")
    
    st.dataframe(filtered_df, use_container_width=True, height=600)
