from pydantic import BaseModel, EmailStr,validator
from typing import List, IO, Union, Any
from starlette.datastructures import  UploadFile
import  os
from mimetypes import MimeTypes
from fastapi_mail.errors import WrongFile



class MessageSchema(BaseModel):
    recipients: List[EmailStr]
    attachments: List[Any] = []
    subject: str = ""
    body: str = None
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    charset: str = "utf-8"
    subtype: str = "plain"


    @validator("attachments")
    def validate_file(cls,v):
        temp = []
        mime = MimeTypes()
                    
        for file in v:
            if isinstance(file,str):

                if os.path.isfile(file) and os.access(file, os.R_OK) and validate_path(file):
                    mime_type = mime.guess_type(file)
                    with open(file,mode="rb") as f:
                        u = UploadFile(f.name,f.read(),content_type=mime_type[0])
                        temp.append(u)
                else:
                    raise  WrongFile("incorrect file path for attachment or not readable")
            elif isinstance(file,UploadFile):
                temp.append(file)
            else:
                raise  WrongFile("attachments field type incorrect, must be UploadFile or path")
        return temp



def validate_path(path):
    cur_dir = os.path.abspath(os.curdir)
    requested_path = os.path.abspath(os.path.relpath(path, start=cur_dir))
    common_prefix = os.path.commonprefix([requested_path, cur_dir])
    return common_prefix == cur_dir

