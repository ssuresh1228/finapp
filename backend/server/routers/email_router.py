from server.util.email_utils import EmailSchema, default_checker
from fastapi_mail import MessageType, MessageSchema, FastMail
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
import server.util.user_manager as user_manager
router = APIRouter()

# sends an email with jinja2 HTML template 
@router.post("/email")
async def send_email_template(email: EmailSchema) -> JSONResponse:
    message = MessageSchema(
        subject = "FastAPI-mail module",
        recipients = email.dict().get("body"),
        subtype = MessageType.html
    )
    fast_mail = FastMail(conf)
    await fast_mail.send_message(message, "signup.html")
    return JSONResponse(status_code=200, content={"message":"email sent"})