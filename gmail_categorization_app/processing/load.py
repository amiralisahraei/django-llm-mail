from django.utils import timezone
from gmail_categorization_app.processing.sentiment_analysis import model_response
from gmail_categorization_app.models import EmailMessage  

def load_data_into_csv(email_data, user_email):
    """
    Convert the provided data into a DataFrame and save it as a CSV file.
    Prevents duplicate emails by checking subject and body.
    """
    for email in email_data:
        subject = email.get('subject', '')
        body = email.get('body', '')
        
        # Check if email already exists
        exists = EmailMessage.objects.filter(
            user_email=user_email,
            subject=subject,
            body=body
        ).exists()
        
        today_date = timezone.now()
        if not exists:
            sentiment_result = model_response(body)

            EmailMessage.objects.create(
                user_email=user_email,
                subject=subject,
                body=body,
                sentiment=sentiment_result,
                received_at=today_date
            )
        else:
            EmailMessage.objects.filter(
                user_email=user_email,
                subject=subject,
                body=body
            ).update(
                received_at=today_date,
            )
