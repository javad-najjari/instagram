import smtplib
from email.message import EmailMessage


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'javad.n077@gmail.com'
EMAIL_PORT_SSL = 465
EMAIL_HOST_PASSWORD = 'cvveluwegjiaenal'
DEFAULT_FROM_EMAIL = 'META'



def send_otp_code(email, code):
    msg = EmailMessage()
    msg['Subject'] = 'confirm email'
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = email
    msg.set_content(f'you can confirm your email by this code: {code}')

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT_SSL) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)

