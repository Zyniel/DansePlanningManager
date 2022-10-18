import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS_FILE = r"./auth/credentials.google.json"
TOKEN_FILE = r"./auth/token.google.txt"


def get_session():
    creds = None
    # The token file  stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as creds:
            creds = pickle.load(token)
            print("Already Authenticated!")
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
        
        print("Authenticated!")

    return creds


def get_calendar_service(creds):
    if creds is None:
        raise RuntimeError("Sessions credentials are not valid !")

    service = build("docs", "v3", credentials=creds)
    return service


def get_storage_service(creds):
    if creds is None:
        raise RuntimeError("Sessions credentials are not valid !")

    service = build("drive", "v3", credentials=creds)
    return service