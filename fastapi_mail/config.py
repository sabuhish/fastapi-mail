import os
from typing import Any
from pydantic import BaseSettings as Settings, conint
from pydantic import EmailStr, validator
from jinja2 import Environment, FileSystemLoader
from fastapi_mail.schemas import validate_path
from fastapi_mail.errors import TemplateFolderDoesNotExist


class ConnectionConfig(Settings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 465
    MAIL_SERVER: str
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True
    MAIL_DEBUG: conint(gt=-1, lt=2) = 0
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str = None
    TEMPLATE_FOLDER: Any = None
    SUPPRESS_SEND: conint(gt=-1, lt=2) = 0
    USE_CREDENTIALS: bool = True

    @validator("TEMPLATE_FOLDER", pre=True)
    def create_template_engine(cls, v):
        template_env = None
        if isinstance(v, str):
            if not os.path.exists(v):
                raise TemplateFolderDoesNotExist(
                    f"{v} is not a valid path to an email template folder")

            if os.path.isdir(v) and os.access(v, os.R_OK) and validate_path(v):
                template_env = Environment(
                    loader=FileSystemLoader(v))
        return template_env
