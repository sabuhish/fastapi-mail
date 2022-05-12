from enum import Enum
from abc import ABC, abstractmethod
import aiosmtplib
import blinker
from pydantic import BaseSettings as Settings

from fastapi_mail.config import ConnectionConfig
from fastapi_mail.dev_server import dev_controller
from fastapi_mail.errors import ConnectionErrors, PydanticClassRequired


class ConnectionEnum(Enum):
    PROD = "prod"
    DEV = "dev"
    TEST = "test"


class BaseConnection(ABC):
    @property
    @abstractmethod
    def session(self):
        raise NotImplemented

    @abstractmethod
    async def __aenter__(self):
        raise NotImplemented

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplemented

    @abstractmethod
    async def _connect(self):
        raise NotImplemented


class ProdConnection(BaseConnection):
    def __init__(self, settings: Settings):
        if not issubclass(settings.__class__, Settings):
            raise PydanticClassRequired(
                """\r
                Email configuration should be provided from ConnectionConfig class, \r
                check example below:

                from fastmail import ConnectionConfig
                conf = Connection(
                    MAIL_USERNAME="your_username",
                    MAIL_PASSWORD="your_pass",
                    MAIL_FROM="your_from_email",
                    MAIL_PORT=587,
                    MAIL_SERVER="email_service",
                    MAIL_TLS=True,
                    MAIL_SSL=False
                )
                """
            )
        self.settings = settings.dict()
        self._session = aiosmtplib.SMTP(
            hostname=self.settings.get("MAIL_SERVER"),
            port=self.settings.get("MAIL_PORT"),
            use_tls=self.settings.get("MAIL_SSL"),
            start_tls=self.settings.get("MAIL_TLS"),
            validate_certs=self.settings.get("VALIDATE_CERTS"),
        )

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        return self._session

    async def __aenter__(self):
        self.session = await self._configure_connection()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return await self.session.quit()

    async def _connect(self):
        return await self.session.connect()

    async def _email_login(self, username: str, password: str):
        if self.settings.get("USE_CREDENTIALS"):
            return await session.login(username, password)

    async def _configure_connection(self):
        try:
            await self._connect()
            await self._email_login(
                self.setting.MAIL_USERNAME, self.setting.MAIL_PASSWORD
            )
            return self.session
        except Exception as error:
            raise ConnectionErrors(
                f"Exception raised {error}, check your credentials or email service configuration"
            )


class DevConnection(BaseConnection):
    def __init__(self, settings: Settings):
        self.settings = settings
        if not issubclass(settings.__class__, Settings):
            raise PydanticClassRequired(
                """\r
                Email configuration should be provided from ConnectionConfig class, \r
                check example below:

                from fastmail import ConnectionConfig
                conf = Connection(
                    MAIL_USERNAME="your_username",
                    MAIL_PASSWORD="your_pass",
                    MAIL_FROM="your_from_email",
                    MAIL_PORT=587,
                    MAIL_SERVER="email_service",
                    MAIL_TLS=True,
                    MAIL_SSL=False
                )
                """
            )

        self._session = aiosmtplib.SMTP(
            hostname=dev_controller.hostname,
            port=dev_controller.port,
        )

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        return self._session

    async def __aenter__(self):
        self.session = await self._configure_connection()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return await self.session.quit()

    async def _connect(self):
        return await self.session.connect()

    async def _configure_connection(self):
        try:
            await self._connect()
            return self.session
        except Exception as error:
            raise ConnectionErrors(
                f"Exception raised {error}, check your credentials or email service configuration"
            )


class ArtificialSession:
    def __init__(self):
        self.email_dispatched = email_dispatched

    async def __aenter__(self):
        return self

    async def __aexit__(self):
        try:
            return await self.quit()
        except Exception:
            pass

    async def send_message(self, msg):
        return self.email_dispatched.send(msg)

    async def quit(self, func):
        return self.email_dispatched.disconnect(func)

    async def connect(self, func):
        return self.email_dispatched.connect(func)


class TestConnection(BaseConnection):
    def __init__(self, settings):
        self._session = ArtificialSession()
        self.outbox = []

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        return self._session

    async def __aenter__(self):
        if not self.session.email_dispatched:
            raise RuntimeError("blinker must be installed")
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return await self.session.quit(self._record)

    async def _connect(self):
        return await self.session.connect(self._record)

    def _record(self, message):
        return self.outbox.append(message)


signals = blinker.Namespace()

email_dispatched = signals.signal(
    "email-dispatched",
    doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""",
)
