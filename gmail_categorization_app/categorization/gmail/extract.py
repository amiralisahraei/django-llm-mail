import base64
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
from gmail_categorization_app.processing.transform import clean_text


def extract_text_from_html(html_content):
    """Extract plain text from HTML content using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return clean_text(soup.get_text(separator='\n'))


def decode_base64_data(data):
    """Decode base64 encoded data."""
    return base64.urlsafe_b64decode(data).decode('utf-8')

def extract_body_from_parts(parts):
    for part in parts:
        if part.get('parts'):
            result = extract_body_from_parts(part['parts'])
            if result:
                return result

        mime_type = part.get('mimeType')
        data = part.get('body', {}).get('data', '')
        if data:
            if mime_type == 'text/plain':
                return clean_text(decode_base64_data(data))
            elif mime_type == 'text/html':
                return extract_text_from_html(decode_base64_data(data))
    return None


def get_email_body(service, msg_id):
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message.get('payload', {})

        parts = payload.get('parts', [])
        if parts:
            return extract_body_from_parts(parts)

        # If no parts, check the main payload directly
        mime_type = payload.get('mimeType')
        data = payload.get('body', {}).get('data', '')
        if data:
            if mime_type == 'text/plain':
                return clean_text(decode_base64_data(data))
            elif mime_type == 'text/html':
                return extract_text_from_html(decode_base64_data(data))

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

    return "No content found"


def list_emails(service, num_messages=20, status='all'):
    """List emails based on read/unread status and return their subject and body."""
    email_data = []
    try:
        query = {
            'read': "is:read category:primary",
            'unread': "is:unread category:primary",
            'all': "category:primary"
        }.get(status, "category:primary")

        messages = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query).execute()

        for message in messages.get('messages', [])[:num_messages]:
            msg_id = message['id']
            msg = service.users().messages().get(userId='me', id=msg_id).execute()

            subject = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), "No Subject")
            body = get_email_body(service, msg_id) or "No Body"

            email_data.append({'subject': subject, 'body': body})

        return email_data
    except HttpError:
        return None
