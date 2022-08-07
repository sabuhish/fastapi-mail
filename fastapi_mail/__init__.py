from fastapi_mail.config import ConnectionConfig
from fastapi_mail.fastmail import FastMail
from fastapi_mail.schemas import MessageSchema, MultipartSubtypeEnum

from . import email_utils

__version__ = '1.1.4'


__author__ = 'sabuhi.shukurov@gmail.com'


__all__ = ['FastMail', 'ConnectionConfig', 'MessageSchema', 'email_utils', 'MultipartSubtypeEnum']
