from pydantic import BaseModel, EmailStr,validator
from typing import List, IO, Union, Any
from fastapi import UploadFile
import  os

class MessageSchema(BaseModel):
    receipients: Union[List[EmailStr],EmailStr]
    attachments: List[Any] = []
    subject: str = ""
    body: str = None
    html: str = None
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    charset: str = "utf-8"

    @validator("attachments")
    def validate_file(cls,v):
        temp = []
        for file in v:
            if isinstance(file,str):
                    if os.path.isfile(file) and os.access(file, os.R_OK):
                        with open(file,mode="br") as f:
                            u = UploadFile(f.name,f.read())
                            temp.append(u)
                    else:
                        raise  ValueError("incorrect file path for attachment or not readable")
            elif isinstance(file,UploadFile):
                temp.append(file)
            else:
                raise  ValueError("attachments field type incorrect, must be UploadFile or path")
        return temp

"""
f = open("pipfile",mode="rb")

u = UploadFile(f.name,f.read())
f.close()

m = MessageSchema(
    sender="test@mail.ru",
    subject="",
    receipients=["test@mail.ru"],
    body="",
    attachments = [u,"setup.py"],
    html = '<span>Hello Outside<span>World</span>End'
    )

print(m.attachments)
"""