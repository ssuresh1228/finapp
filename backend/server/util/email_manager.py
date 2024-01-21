from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pathlib import Path
from server.schemas.user_schema import UserEmailValidator

class EmailManager:
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

    # and sends verification email to user's email address
    # url routes to frontend 
    async def send_verification_email(self, user_email: UserEmailValidator, verify_token: str):
        verification_url = f"http://localhost:3000/auth/verify?verify_token={verify_token}"
        body = {"verification_url": verification_url}
        message = MessageSchema(
            subject = "Verify your account",
            recipients=[user_email],
            template_body=body, 
            subtype=MessageType.html
        )
        await self.fastmail.send_message(message, template_name="user_verification.html")
    
    # sends user email with link to reset password 
    # url routes to frontend
    async def send_password_reset_email(self, user_email: UserEmailValidator, reset_token:str):
        reset_url = f"http://localhost:3000/auth/reset_password?reset_token={reset_token}"
        body = {"reset_url": reset_url}
        message = MessageSchema (
            subject = "Reset your password",
            recipients = [user_email],
            template_body = body, 
            subtype = MessageType.html
        )
        await self.fastmail.send_message(message, template_name="reset_password_link.html")
        
    # sends email confirming password change
    async def send_password_change_confirmation(self, user_email: UserEmailValidator):
        body = {}
        message = MessageSchema(
            subject = "Your password has been reset",
            recipients = [user_email],
            template_body = body,
            subtype = MessageType.html
        )
        await self.fastmail.send_message(message, template_name = "confirm_password_reset.html")