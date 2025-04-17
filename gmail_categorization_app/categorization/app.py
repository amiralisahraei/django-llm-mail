import os
from datetime import datetime

from gmail_categorization_app.categorization.gmail.authenticate_gmail import authenticate_gmail
from gmail_categorization_app.categorization.gmail.extract import list_emails
from gmail_categorization_app.processing.load import load_data_into_csv

# Ensure the output directory exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Moves one level up
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Create if it doesn’t exist

def process_emails(user_email):
    """Authenticate Gmail, extract emails, and load data into CSV."""
    service = authenticate_gmail()
    email_data = list_emails(service)
    load_data_into_csv(email_data, user_email)

def log_current_time():
    """Log the current time in HH:MM:SS format."""
    time_str = datetime.now().strftime("%H:%M:%S")
    print(f"Waiting for 5 minutes before the next execution, current time: {time_str}")

def main(user_email):
    """Run the email processing task."""
    process_emails(user_email)

if __name__ == '__main__':
    main()
