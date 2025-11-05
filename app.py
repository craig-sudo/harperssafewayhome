# PRO SE VERITAS: Streamlit Dashboard Core
# File: app.py (Main Interface)

import streamlit as st
import hashlib
import time
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import tempfile
import json

# --- Firebase Initialization (Singleton Pattern for Streamlit) ---
# This pattern prevents re-initializing the app on every script rerun.
if not firebase_admin._apps:
    # --- TEMPORARY SIMULATION MODE ---
    # For now, we will only initialize Firestore to avoid Storage billing requirements.
    # The `storage_bucket` parts are commented out.
    if "FIREBASE_SERVICE_ACCOUNT_KEY" in st.secrets:
        cred_dict = st.secrets["FIREBASE_SERVICE_ACCOUNT_KEY"]
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred) # Removed storageBucket init
    elif "FIREBASE_SERVICE_ACCOUNT_KEY" in os.environ:
        cred_str = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
        cred_dict = json.loads(cred_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred) # Removed storageBucket init
    else:
        firebase_admin.initialize_app()

db = firestore.client()
# bucket = storage.bucket() # --- TEMPORARILY DISABLED ---


# --- Branding and Setup ---
st.set_page_config(
    page_title="Pro Se Veritas: Legal Evidence Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("⚖️ Pro Se Veritas: Evidence & Integrity Engine")
st.subheader("Created for Harper, perfected for you.")
st.markdown("---")


# --- BACKEND LOGIC INTEGRATION (FROM SERVER-SIDE CODE) ---

def calculate_sha256_of_uploaded_file(uploaded_file):
    """
    Saves the uploaded file to a temp location, then calculates its SHA-256 hash
    by reading in 4KB chunks, mirroring the server-side integrity logic.
    """
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, uploaded_file.name + str(time.time()))
    
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    hash_sha256 = hashlib.sha256()
    try:
        with open(temp_file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        calculated_hash = hash_sha256.hexdigest()
    finally:
        os.remove(temp_file_path)

    return calculated_hash


def process_and_log_evidence(uploaded_file, file_hash):
    """
    SIMULATION MODE: Skips actual upload but logs metadata to Firestore.
    """
    case_id = st.session_state.case_id

    if not uploaded_file:
        return "Error: No file provided.", None
    
    # Temp file is still needed for hashing, but not for upload in this mode.
    # We can remove the second temp file creation.

    try:
        # --- UPLOAD SIMULATION ---
        # The actual upload is commented out. We create a placeholder path.
        storage_path = f"simulated/evidence/{case_id}/raw/{file_hash}-{uploaded_file.name}"
        # destination_blob_name = f"evidence/{case_id}/raw/{file_hash}-{uploaded_file.name}"
        # blob = bucket.blob(destination_blob_name)        
        # blob.upload_from_filename(temp_file_path)
        
        # --- FIRESTORE LOGGING (Still active) ---
        doc_ref = db.collection('cases').document(case_id).collection('evidence').document(file_hash)
        
        evidence_data = {
            "file_name": uploaded_file.name,
            "file_size_bytes": uploaded_file.size,
            "sha256_hash": file_hash,
            "storage_path": storage_path, # Log the simulated path
            "timestamp": firestore.SERVER_TIMESTAMP,
            "verified": True,
            "status": "SHA-256 Verified (Local Simulation - NO UPLOAD)"
        }
        
        doc_ref.set(evidence_data, merge=True)
        
        return f"Success (Simulation): '{uploaded_file.name}' hash verified and logged.", evidence_data

    except Exception as e:
        return f"A critical error occurred during simulation: {e}", None
    # No 'finally' needed to remove temp file as it's handled in the hash function


# --- UI FLOW & REFINED OUTPUT ---

def main_app():
    if 'case_id' not in st.session_state:
        st.session_state.case_id = "PSV-CASE-" + str(int(time.time()))

    st.info(f"Active Case ID (for data separation): **{st.session_state.case_id}**")

    uploaded_files = st.file_uploader(
        "Upload Digital Evidence (PDFs, Images, Videos, etc.)", 
        type=None, 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Process & Secure Evidence", type="primary"):
            st.warning("Running in Simulation Mode: Files are NOT being uploaded to cloud storage.", icon="⚠️")
            with st.spinner("Calculating Integrity Fingerprints and Logging Metadata..."):
                results = []
                for file in uploaded_files:
                    try:
                        hash_value = calculate_sha256_of_uploaded_file(file)
                        status_message, data = process_and_log_evidence(file, hash_value)
                        
                        results.append({
                            "File": file.name,
                            "Status": "Success (Simulation)",
                            "Message": status_message,
                            "Data": data
                        })
                    except Exception as e:
                        results.append({
                            "File": file.name,
                            "Status": "Error",
                            "Message": f"A local processing error occurred: {e}",
                            "Data": None
                        })

            st.success("Evidence Processing Simulation Complete!")
            
            st.markdown("### 📋 Evidence Processing Log")
            for result in results:
                status_icon = "✅" if "Success" in result["Status"] else "❌"
                with st.expander(f'{status_icon} **{result["File"]}** - Status: {result["Status"]}', expanded= "Success" not in result["Status"]):
                    st.markdown(f"**Message:** `{result['Message']}`")
                    if result["Data"]:
                        st.json({
                            "File Name": result["Data"]["file_name"],
                            "SHA-256 Hash": result["Data"]["sha256_hash"],
                            "Size (Bytes)": result["Data"]["file_size_bytes"],
                            "Firebase Storage Path": result["Data"]["storage_path"],
                            "Status": result["Data"]["status"]
                        })

if __name__ == "__main__":
    main_app()
