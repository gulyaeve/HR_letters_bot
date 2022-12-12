from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from logging import log, INFO
from config import Config

Email = Config.Email


async def send_email(recipient, subject, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        await aiosmtplib.send(message=msg,
                              sender=Email.sender_email,
                              recipients=recipient,
                              hostname=Email.email_server,
                              port=Email.email_port,
                              username=Email.email_login,
                              password=Email.email_password,
                              timeout=1,
                              start_tls=True)
        log(msg=f"Success email[{recipient}]: {message}", level=INFO)
    except Exception as _ex:
        log(msg=f"{Exception}: {_ex}: Failed to send email[{recipient}]", level=INFO)


async def send_email_photo(recipient, subject, message, file):
    try:
        msg = MIMEMultipart()
        text = MIMEText(message)
        msg.attach(text)
        msg["Subject"] = subject
        image = MIMEImage(file)
        msg.attach(image)
        await aiosmtplib.send(message=msg,
                              sender=Email.sender_email,
                              recipients=recipient,
                              hostname=Email.email_server,
                              port=Email.email_port,
                              username=Email.email_login,
                              password=Email.email_password,
                              timeout=1,
                              start_tls=True)
        log(msg=f"Success email[{recipient}]", level=INFO)
    except Exception as _ex:
        log(msg=f"{Exception}: {_ex}: Failed to send email[{recipient}]", level=INFO)
