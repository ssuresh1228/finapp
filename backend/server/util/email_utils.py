from fastapi import FastAPI
from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any
from pathlib import Path

#TODO: configure Jinja2 templates folder with actual html 

# use Jinja2 HTML templates 
class EmailSchema(BaseModel):
    email: List[EmailStr]
    template_name: str
    body: Dict[str, Any]

# email sender config
conf = ConnectionConfig(
    MAIL_USERNAME = "username",
    MAIL_PASSWORD = "password",
    MAIL_FROM = "myEmail@email.com",
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
    MAIL_PORT = 465 
)

async def default_checker():
    checker = DefaultChecker(db_provider="redis")
    await checker.init_redis()
    return checker