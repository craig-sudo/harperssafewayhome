# auto_filing_bot.py

import subprocess
import os
import shutil
import time
from pathlib import Path

# --- Configuration ---
# Your Firebase Service Account Key file name
# Place this JSON file in the 'config/' folder of your project
FIREBASE_KEY_FILE = 'config/harpers-safeway-home-firebase-adminsdk-abc12.json'
def run_script(script_name, args="", check_output=False):
    """Helper function to run the existing project scripts."""
    print(f"\n--- Running: {script_name} {args} ---")
    try:
        command = ["python", "-u", str(script_name)] + args.split()
        if check_output:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"--- SUCCESS: {script_name} finished ---")
            return result.stdout
        else:
            subprocess.run(command, check=True)
            print(f"--- SUCCESS: {script_name} finished ---")
            return ""
    except subprocess.CalledProcessError as e:
        print(f"--- ERROR: {script_name} failed. ---")
        print(f"Command: {e.cmd}")
        print(f"Return Code: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        raise # Re-raise the exception to stop the bot

def setup_environment():
    """Sets environment variables needed for Firebase (Phase 2)."""
    if os.path.exists(FIREBASE_KEY_FILE):
        print("Setting up Firebase credentials...")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = FIREBASE_KEY_FILE
    else:
        print(f"WARNING: Firebase key {FIREBASE_KEY_FILE} not found. Skipping cloud integration. Please ensure it's in the 'config/' folder.")

def automate_exhibit_package():
    """
    Main function to run the 3-phase automated filing process.
    """
    print("🤖 AUTO-FILING BOT STARTED")
    setup_environment()
    
    # --- PHASE 1: OCR, Organization, and Renaming ---
    print("\n[PHASE 1/3] Running Core OCR and Organization...")
    # 1. Run the primary evidence processor (to generate the core CSV data)
    # This script should generate a CSV in the 'output' folder. We need to find its name.
    run_script("evidence_processor.py") 
    
    # Assuming evidence_processor.py creates a CSV like 'harper_evidence_results_YYYYMMDD_HHMMSS.csv'
    # We need to find the latest one.
    output_folder = Path("output")
    if not output_folder.exists():
        print("ERROR: 'output' folder not found after evidence_processor.py. Exiting.")
        return

    csv_files = sorted(output_folder.glob("harper_evidence_results_*.csv"), key=os.path.getmtime, reverse=True)
    if not csv_files:
        print("ERROR: No evidence CSV found in 'output' folder. Exiting.")
        return
    latest_csv = csv_files[0]
    print(f"Using latest evidence CSV: {latest_csv.name}")

    # 2. Run the smart renamer to organize files based on the new CSV data
    # smart_evidence_renamer.py is assumed to take the latest CSV implicitly or through config
    run_script("smart_evidence_renamer.py") 

    # --- PHASE 2: AI Enrichment (Gemini/Google Integration) ---
    print("\n[PHASE 2/3] Running AI and Data Enrichment...")
    # 3. Analyze the new evidence using Gemini via the AI Analyzer (adjusts relevance codes and priority)
    # ai_legal_analyzer.py is assumed to read the latest processed CSV and update it
    run_script("ai_legal_analyzer.py") 

    # --- PHASE 3: Final Court Package Assembly ---
    print("\n[PHASE 3/3] Generating Court-Admissible Package...")
    
    # 4. Generate the PDF Exhibits and Master Index
    run_script("legal_triage_suite.py", args="--generate-pdfs")

    # 5. Create the final ZIP archive package with all files and reports
    run_script("court_package_exporter.py", args="comprehensive")

    print("\n\n✅ AUTO-FILING BOT COMPLETE!")
    print("Your final exhibit package should be ready in the 'output/court_packages/' folder.")

if __name__ == "__main__":
    automate_exhibit_package()
