from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any, Optional

# use Jinja2 HTML templates 
class EmailSchema(BaseModel):
    email_addresses: List[EmailStr] # email addresses to send mail to 
    body: Optional[Dict[str, Any]] = {}
    
class ForgotPasswordRequest(BaseModel):
    password_email: EmailStr

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str