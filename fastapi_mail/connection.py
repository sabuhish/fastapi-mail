from abc import ABC, abstractmethod
import aiosmtplib
from pydantic import BaseSettings as Settings

from fastapi_mail.config import ConnectionConfig
from fastapi_mail.dev_server import dev_controller
from fastapi_mail.errors import ConnectionErrors, PydanticClassRequired


class Connection:
    """
    Manages Connection to provided email service with its credentials
    """

    def __init__(self, settings: ConnectionConfig):

        if not issubclass(settings.__class__, Settings):
            raise PydanticClassRequired(
                """\
Email configuration should be provided from ConnectionConfig class, \
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
    
    @property
    def session(self):
        return None

    @property
    def debug_mode(self):
        return self.setting.get('MAIL_DEBUG')

    async def __aenter__(self):  # setting up a connection
        self.session = await self._configure_connection()
        return self

    async def __aexit__(self, exc_type, exc, tb):  # closing the connection
        if not self.settings.get('SUPPRESS_SEND'):   # for test environ
            return await self.session.quit()

    async def _configure_connection(self):
        try:
            if self.debug_mode:
                session = DevConnect(settings)
                await session.connect()
                return session

            session = ProdConnect(settings)
            await session.connect()
            if self.settings.get('USE_CREDENTIALS'):
                await session.login(
                    self.settings.get('MAIL_USERNAME'), self.settings.get('MAIL_PASSWORD')
                )

            return session

        except Exception as error:
            raise ConnectionErrors(
                f'Exception raised {error}, check your credentials or email service configuration'
            )


class BaseConnect(ABC):
    async def connect(self):
        if not self.settings.get('SUPPRESS_SEND', None):
            return await self.client.connect()


class ProdConnect(BaseConnect):
    def __init__(self, setting: dict):
        self.settings = settings
        self.client = aiosmtplib.SMTP(
            hostname=self.settings.get('MAIL_SERVER'),
            port=self.settings.get('MAIL_PORT'),
            use_tls=self.settings.get('MAIL_SSL'),
            start_tls=self.settings.get('MAIL_TLS'),
            validate_certs=self.settings.get('VALIDATE_CERTS'),
        )


class DevConnect(BaseConnect):
    def __init__(self, setting: dict):
        aiosmtplib.SMTP(
            hostname=dev_controller.hostname,
            port=dev_controller.port,
        )
