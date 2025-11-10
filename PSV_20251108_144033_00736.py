
# PRO SE VERITAS: Evidence & Integrity Engine Dashboard
# File: streamlit_app.py (Main Interface - DEMO MODE)

import streamlit as st
import hashlib
import time
import os
import tempfile
import pandas as pd 

# --- CORE INTEGRITY & STORAGE FUNCTIONS (DEMO MODE) ---

def calculate_sha256_of_uploaded_file(uploaded_file):
    """Calculates the SHA-256 hash of an uploaded file without saving it permanently."""
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, uploaded_file.name + str(time.time()))
    calculated_hash = None
    
    try:
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer()) 
            
        hash_sha256 = hashlib.sha256()
        with open(temp_file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
            
        calculated_hash = hash_sha256.hexdigest()
        
    except Exception as e:
        st.error(f"Integrity Engine Error during Hashing: {e}")
        
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return calculated_hash

def process_and_log_evidence_mock(uploaded_file, file_hash):
    """Mocks the evidence logging process for the demo."""
    if "evidence_log" not in st.session_state:
        st.session_state.evidence_log = []

    evidence_data = {
        "File Name": uploaded_file.name,
        "SHA-256 Fingerprint": file_hash[:16] + "...",
        "Status": "VERIFIED (Demo)",
        "Full Status": "Integrity confirmed. In a live environment, this would be secured in Firebase.",
        "File Size": f"{uploaded_file.size / (1024 * 1024):.2f} MB",
        "Timestamp": pd.Timestamp.now(tz="UTC")
    }
    
    st.session_state.evidence_log.append(evidence_data)
    return f"Success: Evidence integrity verified for {uploaded_file.name}.", evidence_data

# --- UI TAB FUNCTIONS ---

def setup_ui():
    st.set_page_config(
        page_title="Pro Se Veritas: Legal Evidence Engine",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("⚖️ Pro Se Veritas: Evidence & Integrity Engine")
    st.subheader("Public Demo Mode: No Login Required")
    st.markdown("---")

def upload_evidence_tab():
    st.header("Step 1: Upload & Verify Evidence")
    st.info("This tool calculates a unique SHA-256 fingerprint for each file. This ensures your evidence is authentic and timestamped, making it verifiable in court.")

    uploaded_files = st.file_uploader(
        "Upload Digital Evidence (PDFs, Images, Videos, etc.)", 
        type=None, 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Process & Verify Evidence Integrity", type="primary"):
            with st.spinner("Calculating Integrity Fingerprints..."):
                results_list = []
                
                for file in uploaded_files:
                    st.write(f"Processing: **{file.name}**...")
                    try:
                        hash_value = calculate_sha256_of_uploaded_file(file)
                        
                        if hash_value:
                            status_message, data = process_and_log_evidence_mock(file, hash_value)
                            results_list.append(data)
                        else:
                            st.warning(f"Could not calculate hash for {file.name}.")

                    except Exception as e:
                        st.error(f"An error occurred while processing {file.name}: {e}")

            if results_list:
                st.success("Evidence Processing Complete!")
                st.subheader("📋 Evidence Integrity Log")
                
                # Display the current session's log
                log_df = pd.DataFrame(st.session_state.evidence_log)
                st.dataframe(log_df[["File Name", "SHA-256 Fingerprint", "Status", "File Size", "Timestamp"]], use_container_width=True, hide_index=True)
                
                st.markdown(
                    '''
                    **Integrity Guarantee:** The **SHA-256 Fingerprint** is a unique, unchangeable code. 
                    In a live system, this proves your file has not been altered since the moment it was logged.
                    '''
                )

def evidence_browser_tab():
    st.header("Step 2: Review and Manage Evidence")
    st.info("This is a placeholder for the evidence browser. In the full version, you would see all your verified evidence here, with options to filter, sort, and export.")

    if "evidence_log" in st.session_state and st.session_state.evidence_log:
        st.subheader("Evidence Log from Current Session")
        log_df = pd.DataFrame(st.session_state.evidence_log)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.write("No evidence has been processed in this session yet. Please go to the 'Upload & Verify' tab.")

def main_app():
    """Main function to run the Streamlit application."""
    setup_ui()
    
    if "evidence_log" not in st.session_state:
        st.session_state.evidence_log = []
    
    tab1, tab2 = st.tabs(["🔒 Upload & Verify", "📁 Evidence Browser"])

    with tab1:
        upload_evidence_tab()

    with tab2:
        evidence_browser_tab()

if __name__ == "__main__":
    main_app()
    # Check if running in a managed environment (like Project IDX)
    # by looking for the PORT environment variable.
    if "PORT" in os.environ:
        # In a managed environment, run Streamlit with the correct server settings.
        # This makes the app accessible from the browser.
        # We use os.system to launch streamlit with arguments.
        port = os.environ["PORT"]
        command = f"streamlit run {__file__} --server.port {port} --server.address 0.0.0.0"
        os.system(command)
    else:
        # Otherwise, run the app normally for local development.
        main_app()
