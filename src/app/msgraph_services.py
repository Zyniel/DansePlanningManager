from O365 import Account, MSGraphProtocol, FileSystemTokenBackend
import datetime as dt

CREDENTIALS_FILE = r"./auth/credentials.microsoft.json"
TOKEN_FILE = r"./auth/token.microsoft.txt"

def authenticate(client_id, secret_id):
    credentials = (client_id, secret_id)

    protocol = MSGraphProtocol()
    scopes = ['calendar_all', 'onedrive_all']
    protocol_scopes = protocol.get_scopes_for(scopes)
    token_backend = FileSystemTokenBackend(token_filename=TOKEN_FILE)
    account = Account(credentials, token_backend=token_backend)

    # check for an unexpired token
    if not account.is_authenticated:
        account.authenticate(scopes=protocol_scopes)
        print("Authenticated!")
    else:
        print("Already Authenticated!")

    return account


def get_calendar_service(account):

    # Get schedule service to manage calendars
    schedule = account.schedule()

    return schedule


def get_storage_service(account):

    # Get schedule service to manage calendars
    storage = account.storage()
    drive = storage.get_default_drive()
    
    return drive    
