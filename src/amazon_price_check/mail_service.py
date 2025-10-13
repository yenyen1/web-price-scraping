from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from amazon_price_check.logger import get_logger

logger = get_logger(__name__)


def get_gmail_service(token_path: str, credentials_path: str):
    from google_auth_oauthlib.flow import InstalledAppFlow
    import os.path

    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    return service


def send(service, receiver: str, sender: str, subject: str, content: str):
    from email.message import EmailMessage
    import base64

    message = EmailMessage()
    message["To"] = receiver
    message["From"] = sender
    message["Subject"] = subject
    message.set_content(content)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"raw": raw}
    try:
        send_message = service.users().messages().send(userId="me", body=body).execute()
        return send_message
    except HttpError as error:
        logger.error("HttpError: %s", error)
        return None


def send_email(token, credentials, receiver, sender, subject, body):
    service = get_gmail_service(token, credentials)
    send(service, receiver, sender, subject, body)
