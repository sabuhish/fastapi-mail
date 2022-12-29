from fastapi_mail.config import ConnectionConfig
from fastapi_mail.fastmail import FastMail
from fastapi_mail.schemas import MessageSchema, MessageType, MultipartSubtypeEnum

from . import email_utils

__author__ = "sabuhi.shukurov@gmail.com"

__all__ = [
    "FastMail",
    "ConnectionConfig",
    "MessageSchema",
    "email_utils",
    "MultipartSubtypeEnum",
    "MessageType",
]
