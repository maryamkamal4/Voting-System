from django.conf import settings
from django.core.mail import send_mail

class EmailVerificationSender:
    @staticmethod
    def send_verification_email(username, cnic, token):
        print(username,cnic,token)
        subject = "Account Verification"
        message = f'Hi email.host.user,\n\n' \
                  f'Please verify the account with the following details:\n' \
                  f'Username: {username}\n' \
                  f'CNIC: {cnic}\n' \
                  f'Click the link to verify: http://127.0.0.1:8000/verify/{token}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_HOST_USER]
        send_mail(subject, message, email_from, recipient_list)
