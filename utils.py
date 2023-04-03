import smtplib
from django.conf import settings
from email.message import EmailMessage
from rest_framework.exceptions import ValidationError
from accounts.models import Follow



def send_otp_code(email, code):
    msg = EmailMessage()
    msg['Subject'] = 'confirm email'
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = email
    msg.set_content(f'you can confirm your email by this code: {code}')

    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT_SSL) as server:
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)


def validate_profile_photo_size(image):
    if image.size > 500000:
        raise ValidationError('The maximum file size that can be uploaded is 500 KB.')


def is_user_allowed(auth_user, target_user):
    is_following = Follow.objects.filter(from_user=auth_user, to_user=target_user).exists()
    return auth_user == target_user or is_following or not target_user.private

