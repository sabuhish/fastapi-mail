from pydantic import BaseSettings as Settings
from pydantic import EmailStr


class ConnectionConfig(Settings):

    MAIL_USERNAME:  str
    MAIL_PASSWORD: str 
    MAIL_PORT: int  = 465
    MAIL_SERVER: str 
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True
    MAIL_DEBUG: int = 1
    MAIL_FROM: EmailStr


