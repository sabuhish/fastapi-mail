from typing import List, IO, Dict
from pydantic import EmailStr
from datetime import date
import asyncio
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from schemas import MessageSchema
from email.utils import formatdate, make_msgid
import time
from fastapi import UploadFile
from version import PY3
from email.encoders import encode_base64

class Message:
    """

    Preaparation of class for email text
    
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
        receipients: List[EmailStr] = [],
        attachments: List[IO[bytes]] = [],
        subject: str = "",
        body: str = None,
        html: str = None,
        cc: List[EmailStr] = [],
        bcc: List[EmailStr] = [],
        charset: str = "utf-8"
    ):
        self.receipients = receipients
        self.attachments = attachments
        self.subject = subject
        self.body = body
        self.html = html
        self.cc = cc
        self.bcc = bcc
        self.charset = charset
        self.msgId = make_msgid()


    def _mimetext(self, text, subtype="plain"):
        """Creates a MIMEText object"""
        return MIMEText(text, _subtype=subtype, _charset=self.charset)


    async def attach_file(self, message, attachment):

        print(attachment)
        
        for file in attachment:
        
            print(file)
            part = MIMEBase(*file.content_type.split('/'))
                
            part.set_payload(await file.read())
            encode_base64(part)

            filename = file.filename

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                if not PY3:
                    filename = filename.encode('utf8')

            filename = ('UTF8', '', filename)
            

            part.add_header(
                'Content-Disposition',
                "attachment",
                filename=filename)
            

            self.message.attach(part)


    
    async def _message(self):
        """Creates the email message"""
            
        self.message = MIMEMultipart()
        self.message.set_charset(self.charset)

        self.message['Date'] = formatdate(time.time(), localtime=True)
        self.message['Message-ID'] = self.msgId
        self.message["To"] = ', '.join(list(self.receipients))
        self.message["From"] = "sabuhi.shukurov@gmail.com"



        if self.subject:
            self.message["Subject"] = (self.subject)
           
        if self.cc:
            self.message["Cc"] = ', '.join(list(self.cc))
        
        if self.bcc:
            self.message["Bcc"] = ', '.join(list(self.cc))

        if self.body:
            self.message.attach(self._mimetext(self.body))


        if self.attachments:
            print()
            await self.attach_file(self.message, self.attachments)
            

           
            # AttachFile(self.message, self.attachments)

        print(self.message)

        return self.message

    
    async def as_string(self):
        return await self._message().as_string()
        
    # def as_bytes(self):
    #     return self._message().as_bytes()

    # def __str__(self):
    #     return self.as_string()

    # def __bytes__(self):
    #     return self.as_bytes()

f = open("/home/sebuhi/Documents/fastapi-mail/README.md",mode="rb")

u = UploadFile(f.name,f.read())
f.close()

m = MessageSchema(
    sender="test@mail.ru",
    subject="",
    receipients=["test@mail.ru"],
    body="",
    attachments = [u,"/home/sebuhi/Documents/fastapi-mail/fastapi_mail/fastmail.py"],
    html = '<span>Hello Outside<span>World</span>End'
    )


# m = MessageSchema( sender="test@mail.ru",
#     subject="test subject",
#     receipients=["test@mail.ru"],
#     body="TEstst body",
#     attachments=["/home/sebuhi/Documents/fastapi-mail/fastapi_mail/fastmail.py"])
    
message = Message(
   **m.dict()
)


asyncio.run(message._message())

# print(message.attachments)


