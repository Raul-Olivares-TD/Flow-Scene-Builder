import os
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Grant Permissions: If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def authenticate():
    """Authenticate with Google Drive using the credentials json file."""
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def download_files(files_id, download_dir):
    """Downloads multiple files from Google Drive.
    Args:
        file_ids: List of file IDs to download
        download_dir: Directory path where the files will be saved
    """
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    for file_id in files_id:
        # Get file metadata to preserve original name
        file_metadata = service.files().get(fileId=file_id, fields="name").execute()
        file_name = file_metadata["name"]

        # Set the full path for saving the file
        download_path = os.path.join(download_dir, file_name)

        # Create the download request and file writer
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(download_path, "wb") as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_name}: {int(status.progress() * 100)}% complete")

        print(f"File {file_name} downloaded to {download_path}")


# TESTING DOWNLOAD

# List of file IDs to download
# These IDs files are in my drive
files_id = ['1_Lc9B8smsiBiw02kC1G_-stSS9jwXPK8', '1buSfxRRsrQ8myxyLTYyoxwhzLgtBNtHE',
            '1TUgXVqN0DV3BzqIKgJfMvR2ZTMPz3zKa', '10whGOWhI5cnaTxZrVwK9XxpDmmtDFE7Y',
            '1a9AxfUzIMDbnOFebD2n6o81T06joJ67t']

# Call the function with the directory path where files should be saved
download_files(files_id, "D:\\assets")
