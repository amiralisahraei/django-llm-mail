import re

def clean_text(text):
    """Remove extra spaces, newlines, and links from the extracted text."""
    cleaned_text = re.sub(r'\s+', ' ', text.strip())  # Replace multiple spaces and newlines with a single space
    cleaned_text = re.sub(r'http\S+|www\S+|https\S+', '', cleaned_text)  # Remove links
    return cleaned_text