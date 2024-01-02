from pydantic import EmailStr, BaseModel
from typing import List, Dict, Any, Optional

# use Jinja2 HTML templates 
class EmailSchema(BaseModel):
    email_addresses: List[EmailStr] # email addresses to send mail to 
    #template_name (str): html template to send in message body
    body: Optional[Dict[str, Any]] = {}