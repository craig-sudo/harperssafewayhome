# google_workspace_sync.py
import os
import io
import shutil
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Define the scopes (permissions) needed for Drive and Docs access
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly'
]
CREDENTIALS_FILE = 'config/credentials.json'
TOKEN_FILE = 'config/token.json'
LOCAL_EXTERNAL_DATA_DIR = 'external_data/'

# Ensure the local organization directory exists
os.makedirs(LOCAL_EXTERNAL_DATA_DIR, exist_ok=True)

def authenticate_google_drive():
    """Handles OAuth 2.0 authentication flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            # This line will open the browser for manual login on first run
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next time
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def search_and_download_evidence(service):
    """Searches for key file types (GeoJSON, specific CSVs, Docs) and downloads them."""
    print("Searching Google Drive for external evidence...")
    
    # Define search queries for common external evidence types
    # This query finds GeoJSON, CSV files, and Documents that might contain key words
    search_query = ("mimeType='application/vnd.google-apps.document' or "
                    "name contains 'GeoJSON' or "
                    "name contains 'Email Export' or "
                    "mimeType='application/json' and name contains 'Takeout'")
    
    results = service.files().list(
        q=search_query,
        pageSize=10, 
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print("No specific external evidence files found on Google Drive.")
        return

    for item in items:
        file_name = item['name']
        file_id = item['id']
        file_mime = item['mimeType']
        
        target_path = os.path.join(LOCAL_EXTERNAL_DATA_DIR, file_name)

        if file_mime == 'application/vnd.google-apps.document':
            # Export Google Docs as simple text files
            target_path += '.txt'
            print(f"Downloading Google Doc: {file_name} as {target_path}")
            request = service.files().export(fileId=file_id, mimeType='text/plain')
        else:
            # Download files directly (GeoJSON, CSV)
            print(f"Downloading File: {file_name}")
            request = service.files().get_media(fileId=file_id)

        try:
            fh = io.FileIO(target_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        except HttpError as e:
            print(f"An error occurred during download of {file_name}: {e}")

    print(f"Successfully synced external evidence to {LOCAL_EXTERNAL_DATA_DIR}")

def sync_google_workspace():
    """Main orchestrator function for the Google Drive sync bot."""
    print("--- STARTING GOOGLE WORKSPACE SYNC ---")
    try:
        drive_service = authenticate_google_drive()
        search_and_download_evidence(drive_service)
    except Exception as e:
        print(f"CRITICAL ERROR during Google Workspace sync: {e}")
        print("Please ensure 'config/credentials.json' is correct and try running the script once manually to authorize.")

if __name__ == '__main__':
    sync_google_workspace()