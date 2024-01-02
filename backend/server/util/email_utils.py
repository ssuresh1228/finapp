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
    MAIL_FROM = "fastapi@python.com",
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

fastmail = FastMail(conf)

# sent to user after successful registration (still needs verification)
async def send_user_welcome(email:EmailSchema):
    message = MessageSchema(
        subject = "Thanks for registering!",
        recipients = email.email_addresses,
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name = "welcome.html")

# sends user email to verify themselves
async def send_verification_email(email: EmailSchema, token: str):
    body = {
        "token": token
    }
    message = MessageSchema(
        subject = "Verify your account", 
        recipients = email.email_addresses,
        template_body = body,
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name = "user_verification.html")
    
# sends user email to reset password with embedded token 
async def send_password_reset_email(email: EmailSchema, token: str):
    body = {
        "token": token
    }
    message = MessageSchema (
        subject = "Password Reset",
        recipients = email.email_addresses,
        template_body = email.body, 
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name="reset_password.html")
    
# sends email confirming password change
# TODO: test password confirm email 
async def send_password_change_confirmation(email:EmailSchema):
    message = MessageSchema(
        subject = "Password Reset",
        recipients = email.email_addresses,
        template_body = email.body, 
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name = "confirm_password_reset.html")
    
# sends email confirming user verification 
#TODO: test user verified email
async def send_user_verified_confirmation(email:EmailSchema):
    message = MessageSchema(
        subject = "Verification Successful!",
        recipients = email.email_addresses,
        template_body = email.body, 
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name = "user_verified.html")