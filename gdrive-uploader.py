from __future__ import print_function
import os
import sys
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scope: allows file creation in your Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )

            auth_url, _ = flow.authorization_url(
                access_type='offline',
                prompt='consent'
            )

            print("\n👉 Please go to this URL in your browser:\n")
            print(auth_url, "\n")
            code = input("Paste the authorization code here: ")

            flow.fetch_token(code=code)
            creds = flow.credentials

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def upload_file(file_path, folder_id=None):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    mimetype, _ = mimetypes.guess_type(file_path)
    media = MediaFileUpload(file_path, mimetype=mimetype, resumable=True)

    request = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    )

    print(f" 📤 Uploading: {file_path}")

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            percent = int(status.progress() * 100)
            print(f" ⏳ {percent}% complete", end="\r", flush=True)

    # Clear the progress line and replace with final message
    print(" " * 50, end="\r")  
    print(" ✅ Uploaded Successfully")

    print(f"🔗 Link: {response.get('webViewLink')}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 gdrive-oauth-uploader.py <path_to_file>")
        sys.exit(1)
    upload_file(sys.argv[1])
