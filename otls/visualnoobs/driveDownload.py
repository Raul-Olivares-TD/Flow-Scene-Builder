import hou
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
token_path = "D:\\HoudiniDev\\houdiniTools\\token.json"
cred_path = "D:\\HoudiniDev\\houdiniTools\\credentials.json"

def authenticate():
    """Authenticate with Google Drive using the credentials json file."""
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
              cred_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def download_files(files_id, directory_path, progress_callback,
                   file_name_callback, cancel_callback):
    """Downloads multiple files from Google Drive.
    :param  files_id: List of file IDs to download (list)
    :param directory_path: Directory path where the files will be saved (string)
    :param progress_callback: Save progress data (int)
    :param file_name_callback: Save the file name at each download
    :param cancel_callback: Set the cancel option
    """
    os.makedirs(directory_path, exist_ok=True)

    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    for file_id in files_id:
        if cancel_callback():
            return
        try:
            # Get file metadata to preserve original name
            file_metadata = service.files().get(fileId=file_id, fields="name").execute()
            file_name = file_metadata["name"]

            # Set the full path for saving the file
            download_path = os.path.join(directory_path, file_name)

            # Create the download request and file writer
            request = service.files().get_media(fileId=file_id)
            with io.FileIO(download_path, "wb") as file:
                downloader = MediaIoBaseDownload(file, request, chunksize=1024 * 1024 * 50)
                done = False
                while not done:
                    if cancel_callback():
                        return
                    status, done = downloader.next_chunk()
                    progress = int(status.progress() * 100)
                    progress_callback(progress)
                    file_name_callback(file_name)

        except Exception as e:
            print(f"An error occurred while downloading file {file_id}: {e}")
            continue  # Continue with the netx file if an error ocurred
