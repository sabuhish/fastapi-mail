import aiosmtplib

from fastapi_mail.config import ConnectionConfig
from fastapi_mail.errors import ConnectionErrors, PydanticClassRequired


class Connection:
    """
    Manages Connection to provided email service with its credentials
    """

    def __init__(self, settings: ConnectionConfig) -> None:
        if not isinstance(settings, ConnectionConfig):
            raise PydanticClassRequired(
                "Configuration should be provided from ConnectionConfig class"
            )
        self.settings = settings

    async def __aenter__(self) -> "Connection":
        """
        Setting up a connection
        """
        await self._configure_connection()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Closing the connection
        """
        if not self.settings.SUPPRESS_SEND:  # for test environ
            await self.session.quit()

    async def _configure_connection(self) -> None:
        try:
            self.session = aiosmtplib.SMTP(
                hostname=self.settings.MAIL_SERVER,
                timeout=self.settings.TIMEOUT,
                port=self.settings.MAIL_PORT,
                use_tls=self.settings.MAIL_SSL_TLS,
                start_tls=self.settings.MAIL_STARTTLS,
                validate_certs=self.settings.VALIDATE_CERTS,
                local_hostname=self.settings.LOCAL_HOSTNAME,
                cert_bundle=self.settings.CERT_BUNDLE,
            )

            if not self.settings.SUPPRESS_SEND:  # for test environ
                await self.session.connect()

                if self.settings.USE_CREDENTIALS:
                    await self.session.login(
                        self.settings.MAIL_USERNAME,
                        self.settings.MAIL_PASSWORD.get_secret_value(),
                    )

        except Exception as error:
            raise ConnectionErrors(
                f"Exception raised {error}, check your credentials or email service configuration"
            )
