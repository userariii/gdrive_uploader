from __future__ import print_function
import os
import sys
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Scope: allows file creation in your Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    creds = None
    # Load saved token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If token invalid or missing, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            # Opens a temporary local web server
            creds = flow.run_local_server(port=0)

        # Save the token for future automated runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def upload_file(file_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    mimetype, _ = mimetypes.guess_type(file_path)
    media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)

    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    )

    print(f"📤 Uploading: {file_path}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            percent = int(status.progress() * 100)
            print(f"⏳ {percent}% complete", end="\r", flush=True)

    # Replace progress line with final success message
    print(" " * 50, end="\r")
    print("✅ Uploaded Successfully")
    print(f"🔗 Link: {response.get('webViewLink')}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 gdrive-oauth-uploader.py <file_path>")
        sys.exit(1)
    upload_file(sys.argv[1])
