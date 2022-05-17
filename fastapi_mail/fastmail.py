from contextlib import contextmanager, asynccontextmanager
import warnings
import blinker
from pydantic import BaseModel

from fastapi_mail.config import ConnectionConfig
from fastapi_mail.connection import (
    ProdConnection,
    DevConnection,
    TestConnection,
    ConnectionEnum,
    BaseConnection,
    email_dispatched,
)
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

        warnings.warn(
            "Use ``async_record_messages`` instead of ``record_messages`` for unit testing fastapi-mail, record_messages is deprecated",
            DeprecationWarning,
        )

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
    Fastapi mail system sending mails(individual, bulk) attachments(individual, bulk)

    :param config: Connection config to be passed

    """

    def __init__(self, config: ConnectionConfig, connection: BaseConnection = None,):

        self.config = config
        if connection is None:
            self.connection = self._guess_connection(
                self.config.SUPPRESS_SEND, self.config.MAIL_DEBUG
            )
        elif connection is not None and connection is not issubclass(connection, BaseConnection):
            raise InvalidConnectionObject()

    async def get_mail_template(self, env_path, template_name):
        return env_path.get_template(template_name)

    @staticmethod
    def make_dict(data):
        try:
            return dict(data)
        except ValueError:
            raise ValueError(
                f"Unable to build template data dictionary - {type(data)} "
                "is an invalid source data type"
            )

    async def __prepare_message(self, message: MessageSchema, template=None):
        if template is not None:
            template_body = message.template_body
            if template_body and not message.html:
                if isinstance(template_body, list):
                    message.template_body = template.render({"body": template_body})
                else:
                    template_data = self.make_dict(template_body)
                    message.template_body = template.render(**template_data)

                message.subtype = "html"
            elif message.html:
                if isinstance(template_body, list):
                    message.template_body = template.render({"body": template_body})
                else:
                    template_data = self.make_dict(template_body)
                    message.template_body = template.render(**template_data)
        msg = MailMsg(**message.dict())
        if self.config.MAIL_FROM_NAME is not None:
            sender = f"{self.config.MAIL_FROM_NAME} <{self.config.MAIL_FROM}>"
        else:
            sender = self.config.MAIL_FROM
        return await msg._message(sender)

    async def send_message(
        self,
        message: MessageSchema,
        template_name: str = None,
        connection: BaseConnection = None,
    ):

        if connection is None:
            connection = self._guess_connection(
                self.config.SUPPRESS_SEND, self.config.MAIL_DEBUG
            )
        elif connection is not None and connection is not issubclass(BaseConnection):
            raise InvalidConnectionObject()

        if not issubclass(message.__class__, BaseModel):
            raise PydanticClassRequired(
                """
Message schema should be provided from MessageSchema class, check example below:

from fastmail import MessageSchema

message = MessageSchema(
    subject="subject",
    recipients=["list_of_recipients"],
    body="Hello World",
    cc=["list_of_recipients"],
    bcc=["list_of_recipients"],
    reply_to=["list_of_recipients"],
    subtype="plain",
)
"""
            )

        fn_conn = connection if connection is not None and connection is not issubclass(connection, BaseConnection) else self.connection

        if self.config.TEMPLATE_FOLDER and template_name:
            template = await self.get_mail_template(
                self.config.template_engine(), template_name
            )
            msg = await self.__prepare_message(message, template)
        else:
            msg = await self.__prepare_message(message)

        async with fn_conn(self.config) as client:
            await client.session.send_message(msg)

    @asynccontextmanager
    async def async_record_messages(self):
        connection = self._guess_connection(1, self.config.MAIL_DEBUG)
        async with connection(self.config) as client:
            yield client.outbox

    def _guess_connection(self, suppress_send: int, mail_debug: int):
        guess = ConnectionEnum.PROD
        if suppress_send:
            guess = ConnectionEnum.TEST
        if not suppress_send and mail_debug:
            guess = ConnectionEnum.DEV

        return {
            ConnectionEnum.PROD: ProdConnection,
            ConnectionEnum.DEV: DevConnection,
            ConnectionEnum.TEST: TestConnection,
        }.get(guess, None)
