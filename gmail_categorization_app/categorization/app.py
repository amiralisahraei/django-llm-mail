from gmail_categorization_app.categorization.gmail.authenticate_gmail import authenticate_gmail
from gmail_categorization_app.categorization.gmail.extract import list_emails
from gmail_categorization_app.processing.load import load_data_into_csv

def process_emails(user):
    """Authenticate Gmail, extract emails, and load data into a CSV file."""
    try:
        service = authenticate_gmail(user)
        email_data = list_emails(service)
        load_data_into_csv(email_data, user.email)
    except ValueError as e:
        raise ValueError(f"Gmail authentication error: {e}")

def main(user):
    """Run the email processing task."""
    process_emails(user)

if __name__ == '__main__':
    main()
