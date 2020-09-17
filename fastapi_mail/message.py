from typing import List, IO, Dict
from pydantic import EmailStr
from datetime import date
import asyncio
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from schemas import MessageSchema

class Message:
    """
    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    """
    def __init__(
        self,
        sender: EmailStr,
        receipients: List[EmailStr] = [],
        attachments: List[IO[bytes]] = [],
        subject: str = "",
        body: str = None,
        html: str = None,
        cc: List[EmailStr] = [],
        bcc: List[EmailStr] = [],
        charset: str = "utf-8"
    ):
        self.sender = sender
        self.receipients = receipients
        self.attachments = attachments
        self.subject = subject
        self.body = body
        self.html = html
        self.cc = cc
        self.bcc = bcc
        self.charset = charset


    def _mimetext(self, text, subtype="plain"):
        """Creates a MIMEText object"""
        return MIMEText(text, _subtype=subtype, _charset=self.charset)

        
    def _message(self):
        """Creates the email"""
        
        if self.attachments:
            msg = MIMEMultipart()
            msg = self._mimetext(self.body)
        else:
            msg.attach(self._mimetext(self.body))

        if self.subject:
            msg["Subject"] = self.subject

        if self.sender:
            msg["From"] = self.sender
        
        if self.receipients:
            msg["To"] = ', '.join(list(self.receipients))

        if self.cc:
            msg["Cc"] = ', '.join(list(self.cc))

        return msg

    
    def as_string(self):
        return self._message().as_string()
        
    def as_bytes(self):
        return self._message().as_bytes()

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()


m = MessageSchema( sender="test@mail.ru",
    subject="",
    receipients=["test@mail.ru"],
    body="",
    attachments=["Pipfile"])
    
message = Message(
   **m.dict()
)

print(message.attachments)


