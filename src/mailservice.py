
def get_gmail_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = Credentials.from_authorized_user_file('mailservice/token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(service, reciever: str, sender: str, subject:str, content: str):
    from email.message import EmailMessage
    from googleapiclient.errors import HttpError
    import base64

    message = EmailMessage()
    message['To'] = reciever
    message['From'] = sender
    message['Subject'] = subject
    message.set_content(content)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    try:
        send_message = service.users().messages().send(userId='me', body=create_message).execute()
        return 1
    except HttpError as error:
        return None




