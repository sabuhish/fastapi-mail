from fastapi_mail.config import  ConnectionConfig
from fastapi_mail.connection import Connection
from fastapi_mail.schemas import MessageSchema
from fastapi_mail.msg import MailMsg
import asyncio
import aiosmtplib


class FastMail:
    '''
    Fastapi mail system sending mails(individual, bulk) attachments(individual, bulk)

    '''
    def __init__(self,
        config : ConnectionConfig
        ):

        self.config = config

    async def __preape_message(self, message):
        msg = MailMsg(**message.dict())
        return await msg._message(self.config.MAIL_USERNAME)

    async def send_message(self, message: MessageSchema):
        msg = await self.__preape_message(message)

        async with Connection(self.config) as session:
            await session.session.send_message(msg)


