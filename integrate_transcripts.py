
import csv
import os

def integrate_transcriptions():
    """
    Reads the harper_evidence_backup CSV file and integrates the transcriptions.
    """
    csv_file_path = "secure_backups/harper_evidence_backup_20251021_070813.csv"

    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_name = row.get("File_Name")
            transcription = row.get("Key_Factual_Statement")
            if file_name and transcription:
                print(f"File: {file_name}, Transcription: {transcription[:100]}...") # Print first 100 chars
            else:
                print("Skipping row with missing data")


if __name__ == "__main__":
    integrate_transcriptions()
