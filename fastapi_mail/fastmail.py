from contextlib import contextmanager
from email.message import EmailMessage, Message
from email.utils import formataddr
from typing import Any, Dict, Optional, Union

import blinker
from jinja2 import Environment, Template
from pydantic import EmailStr

from fastapi_mail.config import ConnectionConfig
from fastapi_mail.connection import Connection
from fastapi_mail.errors import PydanticClassRequired
from fastapi_mail.msg import MailMsg
from fastapi_mail.schemas import MessageSchema


class _MailMixin:
    @contextmanager
    def record_messages(self):
        """Records all messages. Use in unit tests for example::
            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"
        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message):
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)


class FastMail(_MailMixin):
    """
    FastMail builds the message from the config
    """

    def __init__(self, config: ConnectionConfig) -> None:
        self.config = config

    async def get_mail_template(
        self, env_path: Environment, template_name: str
    ) -> Template:
        return env_path.get_template(template_name)

    @staticmethod
    def check_data(data: Union[Dict[Any, Any], str, None]) -> Dict[Any, Any]:
        if not isinstance(data, dict):
            raise ValueError(
                f"Unable to build template data dictionary - {type(data)}"
                "is an invalid source data type"
            )

        return data

    async def __prepare_message(
        self, message: MessageSchema, template: Optional[Template] = None
    ) -> Union[EmailMessage, Message]:
        if template and message.template_body is not None:
            message.template_body = await self.__template_message_builder(
                message, template
            )
        msg = MailMsg(message)
        sender = await self.__sender()
        return await msg._message(sender)

    async def __template_message_builder(
        self, message: MessageSchema, template: Template
    ) -> str:
        if isinstance(message.template_body, list):
            return template.render({"body": message.template_body})
        else:
            template_data = self.check_data(message.template_body)
            return template.render(**template_data)

    async def __sender(self) -> Union[EmailStr, str]:
        sender = self.config.MAIL_FROM
        if self.config.MAIL_FROM_NAME is not None:
            return formataddr((self.config.MAIL_FROM_NAME, self.config.MAIL_FROM))
        return sender

    async def send_message(
        self, message: MessageSchema, template_name: Optional[str] = None
    ) -> None:
        if not isinstance(message, MessageSchema):
            raise PydanticClassRequired(
                "Message schema should be provided from MessageSchema class"
            )

        if self.config.TEMPLATE_FOLDER and template_name:
            template = await self.get_mail_template(
                self.config.template_engine(), template_name
            )
            msg = await self.__prepare_message(message, template)
        else:
            msg = await self.__prepare_message(message)

        async with Connection(self.config) as session:
            if not self.config.SUPPRESS_SEND:
                await session.session.send_message(msg)

            email_dispatched.send(msg)


signals = blinker.Namespace()

email_dispatched = signals.signal(
    "email-dispatched",
    doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""",
)
