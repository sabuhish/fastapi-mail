import os
from typing import Any
from pydantic import BaseSettings as Settings
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
    MAIL_DEBUG: int = 0
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str = None
    TEMPLATE_FOLDER: Any = None
    SUPPRESS_SEND: int = 0
    USE_CREDENTIALS: bool = True

    @validator("SUPPRESS_SEND")
    def validate_email_suppression(cls, v):
        if v < 0:
            raise ValueError(f"Expected either 0 or 1, got {v}")
        if v > 1:
            raise ValueError(f"Expected either 0 or 1, got {v}")

    @validator("MAIL_DEBUG")
    def validate_email_debug(cls, v):
        if v < 0:
            raise ValueError(f"Expected either 0 or 1, got {v}")
        if v > 1:
            raise ValueError(f"Expected either 0 or 1, got {v}")

    @validator("TEMPLATE_FOLDER", pre=True)
    def create_template_engine(cls, v):
        template_env = None
        if isinstance(v, str):
            if not os.path.exists(v):
                raise TemplateFolderDoesNotExist(f"{v} is not a valid path to an email template folder")

            if os.path.isdir(v) and os.access(v, os.R_OK) and validate_path(v):
                template_env = Environment(
                    loader=FileSystemLoader(v))
        return template_env
