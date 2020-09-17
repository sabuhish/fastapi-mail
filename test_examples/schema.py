
from pydantic import BaseModel,EmailStr


class EmailSchema(BaseModel):
    email: EmailStr
