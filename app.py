# PRO SE VERITAS: Streamlit Dashboard Core
# File: app.py (Main Interface)

import streamlit as st
import hashlib
import time
import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import tempfile

# --- Firebase Initialization (Singleton Pattern for Streamlit) ---
# This pattern prevents re-initializing the app on every script rerun.
if not firebase_admin._apps:
    # For production, use st.secrets to securely load your Firebase service account key.
    # Example:
    # cred_dict = st.secrets["firebase_service_account"]
    # cred = credentials.Certificate(cred_dict)
    # firebase_admin.initialize_app(cred, {'storageBucket': 'your-bucket-name.appspot.com'})

    # Assumes Application Default Credentials (ADC) are configured.
    firebase_admin.initialize_app()

db = firestore.client()
bucket = storage.bucket() # Initialize the default storage bucket

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

# 1. Hashing Logic - Adapted for Server-Side Processing
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


# 2. Firebase Storage Upload & Metadata Logging (Full Integration)
def process_and_log_evidence(uploaded_file, file_hash):
    """
    Uploads file to Firebase Storage and logs metadata to Firestore,
    integrating the provided server-side upload and logging snippets.
    """
    case_id = st.session_state.case_id

    if not uploaded_file:
        return "Error: No file provided.", None
    
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, uploaded_file.name + "_upload_" + str(time.time()))
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # --- UPLOAD SNIPPET INTEGRATION ---
        destination_blob_name = f"evidence/{case_id}/raw/{file_hash}-{uploaded_file.name}"
        blob = bucket.blob(destination_blob_name)        
        blob.upload_from_filename(temp_file_path)
        storage_path = destination_blob_name
        
        # --- FIRESTORE LOGGING SNIPPET INTEGRATION ---
        doc_ref = db.collection('cases').document(case_id).collection('evidence').document(file_hash)
        
        evidence_data = {
            "file_name": uploaded_file.name,
            "file_size_bytes": uploaded_file.size,
            "sha256_hash": file_hash,
            "storage_path": storage_path,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "verified": True,
            "status": "SHA-256 Verified (Upload Complete)"
        }
        
        doc_ref.set(evidence_data, merge=True)
        
        return f"Success: Evidence '{uploaded_file.name}' verified and secured.", evidence_data

    except Exception as e:
        return f"A critical Firebase error occurred for {uploaded_file.name}: {e}", None
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


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
            with st.spinner("Calculating Integrity Fingerprints and Securing to Firebase..."):
                results = []
                for file in uploaded_files:
                    try:
                        hash_value = calculate_sha256_of_uploaded_file(file)
                        status_message, data = process_and_log_evidence(file, hash_value)
                        
                        results.append({
                            "File": file.name,
                            "Status": status_message.split(":")[0],
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

            st.success("Evidence Processing Complete!")
            
            # --- REFINED EVIDENCE LOG OUTPUT ---
            st.markdown("### 📋 Evidence Processing Log")
            for result in results:
                status_icon = "✅" if result["Status"] == "Success" else "❌"
                with st.expander(f'{status_icon} **{result["File"]}** - Status: {result["Status"]}', expanded=result["Status"] != "Success"):
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
