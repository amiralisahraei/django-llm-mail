from decouple import config, Csv
import os
import re
from langchain_groq import ChatGroq

# Load environment variables from .env file
# dotenv_path = "../.env" 
# load_dotenv(dotenv_path)

# Access environment variables
GROQ_API_KEY = config('GROQ_API_KEY')
MODEL_NAME = config('MODEL_NAME')

# Initialize LLM
def initialize_llm(model_name):
    return ChatGroq(
        model=model_name,
        api_key = GROQ_API_KEY,
        temperature=0.5,
        max_tokens=None,
        timeout=None,
        streaming=True,
    )

llm = initialize_llm(MODEL_NAME)

SYSTEM_ROLE = """
You are a highly intelligent email analysis assistant. Your task is to classify emails into one of the following three categories:

1. Positive — The email is related to a job opportunity or application and indicates a positive outcome (e.g., interview invitation, job offer, follow-up with interest).
2. Negative — The email is related to a job opportunity or application and indicates a negative outcome (e.g., rejection, no further interest, position filled).
3. Other — The email is not related to job applications or job opportunities. This includes newsletters, personal messages, marketing, system notifications, and any unrelated content.

Your response must be only one word: **"Positive"**, **"Negative"**, or **"Other"** — with no additional explanation.

Be strict and accurate. Only classify as "Positive" or "Negative" if the content is clearly about a job application outcome.
"""

def model_response(message, model_name="deepseek-r1-distill-llama-70b"):
    messages = [
        ("system", SYSTEM_ROLE),
        ("human", message),
    ]
    llm = initialize_llm(model_name)
    output = llm.invoke(messages).content
    # Remove the "thinking" part from response
    output = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
    return output

if __name__ == "__main__":
    message = """
    Amirali,

    We appreciate your interest in working at Aristocrat Interactive. Unfortunately, we will not be moving forward with your application for Data Engineer (ID: R0016773) role.

    We encourage you to follow us on LinkedIn so that when other opportunities arise that align with your background and qualifications, you can be among the first to know.

    If you have applied for more than one role, your resume will be reviewed against those position requirements and applicants, and you will be notified separately regarding the outcome.

    We appreciate your passion for Aristocrat Interactive and wish you the best in your job search.

    Thank you, 
    """

    print(model_response(MODEL_NAME, message))