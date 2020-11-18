import os
from typing import Any
from pydantic import BaseSettings as Settings
from pydantic import EmailStr, validator
from fastapi_mail.schemas import validate_path
from jinja2 import Environment, FileSystemLoader


class ConnectionConfig(Settings):

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int = 465
    MAIL_SERVER: str
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True
    MAIL_DEBUG: int = 1
    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str = None
    TEMPLATE_FOLDER: Any = None

    @validator("TEMPLATE_FOLDER", pre=True)
    def create_template_engine(cls, v):
        template_env = None
        if isinstance(v, str):

            if os.path.isdir(v) and os.access(v, os.R_OK) and validate_path(v):
                template_env = Environment(
                    loader=FileSystemLoader(v))
        return template_env
