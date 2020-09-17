from typing import List, IO, Dict
from pydantic import EmailStr
from datetime import date
import asyncio

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


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


    def attach_file(self, msg, attachment):
        return msg.add_header(
                'Content-Disposition', 
                'attachment',
                filename=attachment
            )

        
    def _message(self):
        """Creates the email"""
        
        msg = MIMEMultipart()
        msg.set_charset(self.charset)

        if self.subject:
            msg["Subject"] = (self.subject)

        if self.sender:
            msg["From"] = self.sender
        
        if self.receipients:
            msg["To"] = ', '.join(list(self.receipients))

        if self.cc:
            msg["Cc"] = ', '.join(list(self.cc))
        
        if self.bcc:
            msg["Bcc"] = ', '.join(list(self.cc))

        if self.body:
            msg = self._mimetext(self.body)

        if isinstance(self.attachments, list):
            for attachment in self.attachments:
                self.attach_file(msg, attachment)

        if isinstance(self.attachments, str):
            self.attach_file(msg, attachment)

        return msg

    
    def as_string(self):
        return self._message().as_string()
        
    def as_bytes(self):
        return self._message().as_bytes()

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

    
message = Message(
    sender="sender@python.org",
    subject="Subject message is about python",
    receipients=["r1@gmail.com", "r2@gmail.com"],
    body="Python Tutorials",
    attachments = ["LICENSE", "MANIFEST.in"]
)
message._message()


