from config import  ConnectionConfig
from connection import Connection
from schemas import MessageSchema
from msg import MailMsg
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
        return await msg._message()

    async def send_message(self, message: MessageSchema):
        msg = await self.__preape_message(message)

        async with Connection(self.config) as session:
            await session.send_message(msg)


conf = ConnectionConfig(
    MAIL_USERNAME = "test_user",
    MAIL_PASSWORD = "test123",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False
    )

message = MessageSchema(
    subject="Fastapi mail module",
    receipients=["sebuhi.sukurov.sh@gmail.com", "hasan-555@mail.ru"],
    body="You received this message from vscode :) ",
    attachments = ["testing.py"],
    )

fm = NewFastMail(conf)

asyncio.run(fm.send_message(message))
