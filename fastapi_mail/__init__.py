
from fastapi_mail.fastmail import SendMail
from fastapi_mail.version import VERSION

__author__ = "sabuhi.shukurov@gmail.com"


FastMail = SendMail

__all__ = [
    "FastMail", "VERSION"
]