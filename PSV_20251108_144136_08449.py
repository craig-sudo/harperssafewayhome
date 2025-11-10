
import streamlit as st
import pandas as pd
import os
import tempfile
from evidence_timeline_generator import 
generate_timeline
from utils import load_exhibit_data

st.set_page_config(
    page_title="Master Timeline - Legal Suite",
    page_icon="🕒",
    layout="wide"
)

st.title("🕒 Master Evidence Timeline")
st.write("This page provides a unified, chronological view of all evidence. Upload your own CSV and EML files to merge them into the timeline.")

# --- File Uploader ---
st.sidebar.header("Upload Evidence")
uploaded_files = st.sidebar.file_uploader(
    "Upload CSV or EML files",
    type=['csv', 'eml'],
    accept_multiple_files=True
)

# --- Base Data Loading ---
st.info("Loading main exhibit log...")
exhibit_df = load_exhibit_data()

if exhibit_df.empty:
    st.error("Could not load the primary exhibit file (CUSTODY_COURT_EXHIBITS.txt).")
    base_timeline = pd.DataFrame(columns=['timestamp', 'source', 'event_type', 'details'])
else:
    # Reformat the exhibit data to match the timeline structure
    exhibit_df.rename(columns={'Date/Time': 'timestamp', 'Context': 'details'}, inplace=True)
    exhibit_df['source'] = 'CUSTODY_COURT_EXHIBITS.txt'
    exhibit_df['event_type'] = 'OCR Exhibit'
    exhibit_df['timestamp'] = pd.to_datetime(exhibit_df['timestamp'], errors='coerce')
    base_timeline = exhibit_df[['timestamp', 'source', 'event_type', 'details']].copy()

# --- Process Uploaded Files ---
uploaded_files_timeline = pd.DataFrame()

if uploaded_files:
    st.info(f"Processing {len(uploaded_files)} uploaded file(s)...")
    temp_dir = tempfile.mkdtemp()
    temp_paths = []
    
    try:
        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_paths.append(temp_path)

        # Generate timeline from the temporarily saved files
        if temp_paths:
            uploaded_files_timeline = generate_timeline(temp_paths)
    
    finally:
        # Clean up the temporary directory and files
        for path in temp_paths:
            os.remove(path)
        os.rmdir(temp_dir)

# --- Combine and Display Timeline ---
if not uploaded_files_timeline.empty:
    st.success(f"Successfully processed {len(uploaded_files_timeline)} events from uploaded files.")
    # Ensure columns match for concatenation
    uploaded_files_timeline = uploaded_files_timeline[['timestamp', 'source', 'event_type', 'details']]
    
    combined_timeline = pd.concat([base_timeline, uploaded_files_timeline], ignore_index=True)
else:
    combined_timeline = base_timeline

# Drop rows where timestamp could not be parsed
combined_timeline.dropna(subset=['timestamp'], inplace=True)

# Sort the final timeline
combined_timeline.sort_values(by='timestamp', inplace=True, ascending=False)
combined_timeline.reset_index(drop=True, inplace=True)

# --- Display Timeline ---
st.success(f"Displaying a combined total of **{len(combined_timeline):,}** events.")
st.dataframe(
    combined_timeline,
    use_container_width=True,
    height=700,
    column_config={
        "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD hh:mm:ss A"),
        "source": "Source File",
        "event_type": "Event Type",
        "details": "Details",
    }
)
