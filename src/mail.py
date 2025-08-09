from dotenv import load_dotenv
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()  # loads .env

API_KEY = os.getenv("API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def send_email(subject, body, receiver):
    # Guard clause: prevent sending if config missing
    if not API_KEY or not SENDER_EMAIL:
        print("Email configuration error: Missing API_KEY or SENDER_EMAIL in environment variables.")
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": receiver}],
        sender={"email": SENDER_EMAIL, "name": "Example Sender"},
        subject=subject,
        html_content=body,
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent successfully:", api_response)
        return True
    except ApiException as e:
        print(f"Error sending email: {str(e)}")
        return False
