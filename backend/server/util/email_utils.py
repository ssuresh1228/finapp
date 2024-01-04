from fastapi import FastAPI
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any
from pathlib import Path
from server.schemas.email_schema import EmailSchema
from server.model.user_model import User
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

# helper method for resetting user password
async def get_user_by_email(email:str) -> User:
    user = await User.find_one(User.email == email)
    return user

async def default_checker():
    checker = DefaultChecker(db_provider="redis")
    await checker.init_redis()
    return checker

fastmail = FastMail(conf)

# sends user email with embedded token for verification
async def send_verification_email(email: EmailSchema, verification_url: str):
    body = {
        "verification_url": verification_url
    }
    message = MessageSchema(
        subject = "Verify your account", 
        recipients = email.email_addresses,
        template_body = body,
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name = "user_verification.html")
   
# sends user email to reset password with embedded token 
# routes to frontend
async def send_password_reset_email(email: EmailSchema, reset_url: str):
    body = {
        "reset_url": reset_url
    }
    message = MessageSchema (
        subject = "Reset your password",
        recipients = email.email_addresses,
        template_body = body, 
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name="reset_password.html")
    
# sends email confirming password change
#TODO: handle updating the password field (frontend routes here after user updates password on client)
async def send_password_change_confirmation(email:EmailSchema):
    message = MessageSchema(
        subject = "Your password has been reset",
        recipients = email.email_addresses,
        template_body = email.body, 
        subtype = MessageType.html
    )
    await fastmail.send_message(message, template_name = "confirm_password_reset.html")
    
