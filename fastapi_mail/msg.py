import sys
import time
from email.encoders import encode_base64
from email.message import EmailMessage, Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from typing import Any, Optional, Union

from .schemas import MessageType, MultipartSubtypeEnum

PY3 = sys.version_info[0] == 3


class MailMsg:
    """
    Mail message parameters

    :param: subject: Email subject header
    :param: recipients: List of email addresses
    :param: body: Plain text message or HTML message
    :param: alternative_body: Plain text message or HTML message
    :param: template_body: Data to pass into chosen Jinja2 template
    :param: subtype: MessageType class. Type of body parameter, either "plain" or "html"
    :param: sender: Email sender address
    :param: cc: CC list
    :param: bcc: BCC list
    :param: reply_to: Reply-To list
    :param: attachments: List of attachment instances
    :param: multipart_subtype: MultipartSubtypeEnum instance. Determines the
    nature of the parts of the message and their relationship to each other
    according to the MIME standard
    :param: headers: Dict of custom SMTP headers
    """

    def __init__(self, entries) -> None:
        self.recipients = entries.recipients
        self.attachments = entries.attachments
        self.subject = entries.subject
        self.body = entries.body
        self.alternative_body = entries.alternative_body
        self.template_body = entries.template_body
        self.cc = entries.cc
        self.bcc = entries.bcc
        self.reply_to = entries.reply_to
        self.charset = entries.charset
        self.subtype = entries.subtype
        self.multipart_subtype = entries.multipart_subtype
        self.headers = entries.headers
        self.msgId = make_msgid()

    def _mimetext(self, text: str, subtype: str) -> MIMEText:
        """
        Creates a MIMEText object
        """
        return MIMEText(text, _subtype=subtype, _charset=self.charset)

    async def attach_file(self, message: MIMEMultipart, attachment: Any):
        """
        Creates a MIMEBase object
        """
        for file, file_meta in attachment:
            if file_meta and "mime_type" in file_meta and "mime_subtype" in file_meta:
                part = MIMEBase(
                    _maintype=file_meta["mime_type"], _subtype=file_meta["mime_subtype"]
                )
            else:
                part = MIMEBase(_maintype="application", _subtype="octet-stream")

            part.set_payload(await file.read())
            encode_base64(part)
            await file.close()

            if file_meta and "headers" in file_meta:
                for header in file_meta["headers"].keys():
                    part.add_header(header, file_meta["headers"][header])

            # Add an implicit `Content-Disposition` attachment header,
            #   but only if it wasn't supplied explicitly.
            #   More info here: https://github.com/sabuhish/fastapi-mail/issues/128
            if not part.get("Content-Disposition"):
                filename = file.filename
                try:
                    filename and filename.encode("ascii")
                except UnicodeEncodeError:
                    if not PY3:
                        filename = filename.encode("utf8")

                filename = ("UTF8", "", filename)
                part.add_header("Content-Disposition", "attachment", filename=filename)

            self.message.attach(part)

    def attach_alternative(self, message: MIMEMultipart) -> MIMEMultipart:
        """
        Attaches an alternative body to a given message
        """
        tmpmsg = message
        if self.subtype == MessageType.plain:
            flipped_subtype = "html"
        else:
            flipped_subtype = "plain"
        tmpmsg.attach(self._mimetext(self.alternative_body, flipped_subtype))
        message = MIMEMultipart(MultipartSubtypeEnum.related.value)
        message.set_charset(self.charset)
        message.attach(tmpmsg)
        return message

    async def _message(
        self, sender: Optional[str] = None
    ) -> Union[EmailMessage, Message]:
        """
        Creates the email message
        """

        self.message = MIMEMultipart(self.multipart_subtype.value)
        self.message.set_charset(self.charset)

        if self.template_body:
            self.message.attach(self._mimetext(self.template_body, self.subtype.value))
        elif self.body:
            self.message.attach(self._mimetext(self.body, self.subtype.value))

        if (
            self.alternative_body is not None
            and self.multipart_subtype == MultipartSubtypeEnum.alternative
        ):
            self.message = self.attach_alternative(self.message)

        self.message["Date"] = formatdate(time.time(), localtime=True)
        self.message["Message-ID"] = self.msgId
        self.message["To"] = ", ".join(self.recipients)
        self.message["From"] = sender

        if self.subject:
            self.message["Subject"] = self.subject

        if self.cc:
            self.message["Cc"] = ", ".join(self.cc)

        if self.bcc:
            self.message["Bcc"] = ", ".join(self.bcc)

        if self.reply_to:
            self.message["Reply-To"] = ", ".join(self.reply_to)

        if self.attachments:
            await self.attach_file(self.message, self.attachments)

        if self.headers:
            for header_name, header_content in self.headers.items():
                self.message.add_header(header_name, header_content)

        return self.message

    async def as_string(self) -> Union[EmailMessage, Message]:
        return await self._message()
