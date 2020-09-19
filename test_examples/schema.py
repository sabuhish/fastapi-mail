
from pydantic import BaseModel,EmailStr
from typing import List, Union


class EmailSchema(BaseModel):
    email: List[EmailStr]
