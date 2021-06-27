import os
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings as Settings, conint
from pydantic import EmailStr, validator, DirectoryPath
from jinja2 import Environment, FileSystemLoader

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
    MAIL_FROM_NAME: Optional[str] = None
    TEMPLATE_FOLDER: Optional[DirectoryPath] = None
    SUPPRESS_SEND: conint(gt=-1, lt=2) = 0
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    @validator("TEMPLATE_FOLDER")
    def template_folder_validator(cls, v):
        """Validate the template folder directory."""
        if not v:
            return
        if not os.access(str(v), os.R_OK) or not path_traversal(v):
            raise TemplateFolderDoesNotExist(
                f"{v!r} is not a valid path to an email template folder"
            )
        return v

    def template_engine(self) -> Environment:
        """Return template environment."""
        folder = self.TEMPLATE_FOLDER
        if not folder:
            raise ValueError(
                "Class initialization did not include a ``TEMPLATE_FOLDER`` ``PathLike`` object."
            )
        template_env = Environment(loader=FileSystemLoader(folder))
        return template_env


def path_traversal(fp: Path):
    """Check for path traversal vulnerabilities."""
    base = Path(__file__).parent.parent
    try:
        base.joinpath(fp).resolve().relative_to(base.resolve())
    except ValueError:
        return False
    return True
