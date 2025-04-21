import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmail_categorization_app.models import UserGoogleAuth

def authenticate_gmail(user):
    """
    Get Gmail service for specific user.
    
    Args:
        user: Django User object
    
    Returns:
        Gmail API service object
    
    Raises:
        ValueError: If user is not authenticated with Gmail
        HttpError: If API request fails
    """
    try:
        # Get user's stored credentials
        user_auth = UserGoogleAuth.objects.get(user=user)
        credentials = pickle.loads(user_auth.token)
        
        # Refresh token if expired
        if credentials.expired:
            credentials.refresh(Request())
            user_auth.token = pickle.dumps(credentials)
            user_auth.save()
            
        # Build and return the Gmail service
        return build('gmail', 'v1', credentials=credentials)
    
    except UserGoogleAuth.DoesNotExist:
        raise ValueError('User not authenticated with Gmail')
    except HttpError as error:
        raise HttpError(error.resp, error.content)
