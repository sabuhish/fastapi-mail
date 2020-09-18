
from fastapi_mail.fastmail import FastMail
from fastapi_mail.version import VERSION
from fastapi_mail.config import  ConnectionConfig
from fastapi_mail.schemas import MessageSchema


__author__ = "sabuhi.shukurov@gmail.com"




__all__ = [
    "FastMail", "VERSION", "ConnectionConfig", "MessageSchema", 
]