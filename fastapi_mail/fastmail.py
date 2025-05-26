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
from fastapi_mail.schemas import MessageSchema, MessageType, MultipartSubtypeEnum


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
    def check_data(data: Union[Dict[Any, Any], str, None, list[Any]]) -> Dict[Any, Any]:
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            return {"body": data}
        else:
            raise ValueError(
                f"Unable to build template data dictionary - {type(data)}"
                "is an invalid source data type"
            )

    async def __prepare_message(
        self, message: MessageSchema, template: Optional[Template] = None
    ) -> Union[EmailMessage, Message]:
        if template and message.template_body is not None:
            message.template_body = await self.__template_message_builder(
                message, template
            )
        msg = MailMsg(message)
        sender = await self.__sender(message)
        return await msg._message(sender)

    async def __prepare_html_and_plain_message(
        self,
        message: MessageSchema,
        html_template: Template,
        plain_template: Template,
    ) -> Union[EmailMessage, Message]:
        template_data = self.check_data(message.template_body)
        html = html_template.render(**template_data)
        plain = plain_template.render(**template_data)

        message.multipart_subtype = MultipartSubtypeEnum.alternative
        if message.subtype == MessageType.html:
            message.template_body = html
            message.alternative_body = plain
        else:
            message.template_body = plain
            message.alternative_body = html

        msg = MailMsg(message)
        sender = await self.__sender(message)
        return await msg._message(sender)

    async def __template_message_builder(
        self, message: MessageSchema, template: Template
    ) -> str:
        if isinstance(message.template_body, list):
            return template.render({"body": message.template_body})
        else:
            template_data = self.check_data(message.template_body)
            return template.render(**template_data)

    async def __sender(self, message: MessageSchema) -> Union[EmailStr, str]:
        sender = message.from_email or self.config.MAIL_FROM
        if (from_name := message.from_name or self.config.MAIL_FROM_NAME) is not None:
            return formataddr((from_name, sender))
        return sender

    async def send_message(
        self,
        message: MessageSchema,
        template_name: Optional[str] = None,
        html_template: Optional[str] = None,
        plain_template: Optional[str] = None,
    ) -> None:
        if not isinstance(message, MessageSchema):
            raise PydanticClassRequired(
                "Message schema should be provided from MessageSchema class"
            )

        if self.config.TEMPLATE_FOLDER and (
            template_name or (html_template and plain_template)
        ):
            if template_name:
                template_obj = await self.get_mail_template(
                    self.config.template_engine(), template_name  # type: ignore
                )
                msg = await self.__prepare_message(message, template_obj)
            else:
                html_template_obj = await self.get_mail_template(
                    self.config.template_engine(), html_template or ""  # type: ignore
                )
                plain_template_obj = await self.get_mail_template(
                    self.config.template_engine(), plain_template or ""  # type: ignore
                )
                msg = await self.__prepare_html_and_plain_message(
                    message, html_template_obj, plain_template_obj
                )
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
