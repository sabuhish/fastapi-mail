import sys
import time
import warnings
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

PY3 = sys.version_info[0] == 3


class MailMsg:
    """
    Preaparation of class for email text

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param template_body: Data to pass into chosen Jinja2 template
    :param html: HTML message
    :param subtype: type of body parameter - "plain" or "html". Ignored if
    the html parameter is explicitly specified
    :param sender: email sender address
    :param cc: CC list
    :param bcc: BCC list
    :param reply_to: Reply-To list
    :param attachments: list of Attachment instances
    :param multipart_subtype: MultipartSubtypeEnum instance. Determines the
    nature of the parts of the message and their relationship to each other
    according to the MIME standard
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)
        self.msgId = make_msgid()

    def _mimetext(self, text, subtype='plain'):
        """Creates a MIMEText object"""

        return MIMEText(text, _subtype=subtype, _charset=self.charset)

    async def attach_file(self, message, attachment):
        """Creates a MIMEBase object"""
        for file, file_meta in attachment:
            if file_meta and 'mime_type' in file_meta and 'mime_subtype' in file_meta:
                part = MIMEBase(
                    _maintype=file_meta['mime_type'], _subtype=file_meta['mime_subtype']
                )
            else:
                part = MIMEBase(_maintype='application', _subtype='octet-stream')

            part.set_payload(await file.read())
            encode_base64(part)

            filename = file.filename

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                if not PY3:
                    filename = filename.encode('utf8')

            filename = ('UTF8', '', filename)

            part.add_header('Content-Disposition', 'attachment', filename=filename)
            if file_meta and 'headers' in file_meta:
                for header in file_meta['headers'].keys():
                    part.add_header(header, file_meta['headers'][header])
            self.message.attach(part)

    async def _message(self, sender):
        """Creates the email message"""

        self.message = MIMEMultipart(self.multipart_subtype.value)

        self.message.set_charset(self.charset)
        self.message['Date'] = formatdate(time.time(), localtime=True)
        self.message['Message-ID'] = self.msgId
        self.message['To'] = ', '.join(self.recipients)
        self.message['From'] = sender

        if self.subject:
            self.message['Subject'] = self.subject

        if self.cc:
            self.message['Cc'] = ', '.join(self.cc)

        if self.bcc:
            self.message['Bcc'] = ', '.join(self.bcc)

        if self.reply_to:
            self.message['Reply-To'] = ', '.join(self.reply_to)

        if self.body:
            self.message.attach(self._mimetext(self.body))

        if self.template_body or self.body:
            if not self.html and self.subtype == 'html':
                if self.body:
                    warnings.warn(
                        'Use ``template_body`` instead of ``body`` to pass data into Jinja2 '
                        'template',
                        DeprecationWarning,
                    )
                self.message.attach(self._mimetext(self.template_body or self.body, self.subtype))
            elif self.template_body:
                raise ValueError('tried to send jinja2 template and html')
        elif self.html:
            self.message.attach(self._mimetext(self.html, 'html'))

        if self.attachments:
            await self.attach_file(self.message, self.attachments)

        return self.message

    async def as_string(self):
        return await self._message().as_string()

    def as_bytes(self):
        return self._message().as_bytes()

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()
