from typing import List

from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    email: List[EmailStr]
