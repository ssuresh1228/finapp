from fastapi import FastAPI
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any
from pathlib import Path
from server.schemas.email_schema import EmailSchema

# email sender config
# SMTP server: docker run -p 1080:1080 -p 1025:1025 maildev/maildev
conf = ConnectionConfig(
    MAIL_USERNAME = "python",
    MAIL_PASSWORD = "123",
    MAIL_FROM = "fastapi-mailer@python.com",
    MAIL_FROM_NAME = "fastapi-mail testing",
    MAIL_SERVER = "localhost", #maildev SMTP
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = False,
    TEMPLATE_FOLDER = Path(__file__).parent/'templates',
    MAIL_PORT = 1025, # match MAILDEV_SMTP_PORT
    USE_CREDENTIALS = False,
    MAIL_DEBUG = 1,
    VALIDATE_CERTS = False
)

async def default_checker():
    checker = DefaultChecker(db_provider="redis")
    await checker.init_redis()
    return checker

#TODO: user verification email (called in user_manager.py: on_after_request_password)
async def send_verification_email(email: str, token: str):
    body = {
        "token": token
    }
    message = MessageSchema(
        subject = "Verify your account", 
        recipients = [email],
        template_body = body,
        subtype = MessageType.html
    )
    fastmail = FastMail(conf)
    await fastmail.send_message(message, template_name = "user_verification.html")