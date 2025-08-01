API_KEY="YOUR_API_KEY_HERE"
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def send_mail(subject, message_body, receiver_email):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": receiver_email}],
        sender={"email": "example@example.com", "name": "Example Sender"},
        subject=subject,
        html_content=message_body,
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent successfully:", api_response)
        return True
    except ApiException as e:
        print(f"Error sending daily student report: {str(e)}")
        return False



