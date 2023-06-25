import os
from enum import Enum
from io import BytesIO
from mimetypes import MimeTypes
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr, root_validator, validator
from starlette.datastructures import Headers, UploadFile

from fastapi_mail.errors import WrongFile


class MultipartSubtypeEnum(Enum):
    """
    For more info about Multipart subtypes, visit:
    https://en.wikipedia.org/wiki/MIME#Multipart_subtypes
    """

    mixed = "mixed"
    digest = "digest"
    alternative = "alternative"
    related = "related"
    report = "report"
    signed = "signed"
    encrypted = "encrypted"
    form_data = "form-data"
    mixed_replace = "x-mixed-replace"
    byterange = "byterange"


class MessageType(Enum):
    plain = "plain"
    html = "html"


class MessageSchema(BaseModel):
    recipients: List[EmailStr]
    attachments: List[Union[UploadFile, Dict, str]] = []
    subject: str = ""
    body: Optional[Union[str, list]] = None
    alternative_body: Optional[str] = None
    template_body: Optional[Union[list, dict, str]] = None
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    reply_to: List[EmailStr] = []
    charset: str = "utf-8"
    subtype: MessageType
    multipart_subtype: MultipartSubtypeEnum = MultipartSubtypeEnum.mixed
    headers: Optional[Dict] = None

    @validator("attachments")
    def validate_file(cls, v):
        temp = []
        mime = MimeTypes()

        for file in v:
            file_meta = None
            if isinstance(file, dict):
                keys = file.keys()
                if "file" not in keys:
                    raise WrongFile('missing "file" key')
                file_meta = dict.copy(file)
                del file_meta["file"]
                file = file["file"]
            if isinstance(file, str):
                if os.path.isfile(file) and os.access(file, os.R_OK):
                    mime_type = mime.guess_type(file)
                    with open(file, mode="rb") as f:
                        _, file_name = os.path.split(f.name)
                        content_type = mime_type[0]
                        headers = None
                        if content_type:
                            headers = Headers({"content-type": content_type})
                        file_content = BytesIO(f.read())
                        u = UploadFile(
                            filename=file_name, file=file_content, headers=headers
                        )
                        temp.append((u, file_meta))
                else:
                    raise WrongFile(
                        "incorrect file path for attachment or not readable"
                    )
            elif isinstance(file, UploadFile):
                temp.append((file, file_meta))
            else:
                raise WrongFile(
                    "attachments field type incorrect, must be UploadFile or path"
                )
        return temp

    @root_validator
    def validate_alternative_body(cls, values):
        """
        Validate alternative_body field
        """
        if (
            values["multipart_subtype"] != MultipartSubtypeEnum.alternative
            and values["alternative_body"]
        ):
            values["alternative_body"] = None
        return values

    class Config:
        arbitrary_types_allowed = True
