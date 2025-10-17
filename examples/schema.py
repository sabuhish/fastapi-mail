from typing import List

from pydantic import BaseModel, EmailStr, NameEmail


class EmailSchema(BaseModel):
    email: List[
        NameEmail
    ]  # Now supports both "user@example.com" and "Name <user@example.com>" formats
