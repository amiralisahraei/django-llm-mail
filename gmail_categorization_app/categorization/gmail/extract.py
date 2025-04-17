import base64
import os
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from gmail_categorization_app.processing.transform import clean_text


def extract_text_from_html(html_content):
    """Extract plain text from HTML content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator='\n')  # Get the text and separate paragraphs with newlines
    return clean_text(text_content)

def decode_base64_data(data):
    """Decode base64 encoded data."""
    return base64.urlsafe_b64decode(data).decode('utf-8')

def get_email_body(service, msg_id):
    """Fetch the email body and extract clean plain text from HTML if the email is HTML."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message.get('payload', {})

        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part['mimeType']
                data = part['body'].get('data', '')
                if mime_type == 'text/plain':
                    return clean_text(decode_base64_data(data))
                elif mime_type == 'text/html':
                    return extract_text_from_html(decode_base64_data(data))

        mime_type = payload.get('mimeType')
        data = payload.get('body', {}).get('data', '')
        if mime_type == 'text/plain':
            return clean_text(decode_base64_data(data))
        elif mime_type == 'text/html':
            return extract_text_from_html(decode_base64_data(data))

    except HttpError as error:
        return None

    return "No content found"

def list_emails(service, num_messages=20, status='all'):
    """List emails based on read/unread status and return their subject and body."""
    email_data = []
    try:
        if status == 'read':
            query = "is:read category:primary"
        elif status == 'unread':
            query = "is:unread category:primary"
        elif status == 'all':
            query = "category:primary"
        messages = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()

        for message in messages.get('messages', [])[:num_messages]:
            msg_id = message['id']
            msg = service.users().messages().get(userId='me', id=msg_id).execute()

            subject = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), "No Subject")
            body = get_email_body(service, msg_id) or "No Body"

            email_data.append({'subject': subject, 'body': body})

        return email_data
    except HttpError as error:
        return None

