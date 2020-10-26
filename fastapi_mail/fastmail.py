from fastapi_mail.config import  ConnectionConfig
from fastapi_mail.connection import Connection
from fastapi_mail.schemas import MessageSchema
from fastapi_mail.msg import MailMsg
import asyncio
import aiosmtplib
from pydantic import BaseModel


class FastMail:
    '''
    Fastapi mail system sending mails(individual, bulk) attachments(individual, bulk)

    :param config: Connection config to be passed

    '''
    def __init__(self,
        config : ConnectionConfig
        ):

        self.config = config

    async def __preape_message(self, message):
        msg = MailMsg(**message.dict())
        return await msg._message(self.config.MAIL_FROM)

    async def send_message(self, message: MessageSchema):

        if not issubclass(message.__class__,BaseModel):
            raise  PydanticClassRequired('''Message schema should be provided from MessageSchema class, check example below:
         \nfrom fastmail import MessageSchema  \nmessage = MessageSchema(\nsubject = "subject",\nrecipients= ["list_of_recipients"],\nbody = "Hello World",\ncc = ["list_of_recipients"],\nbcc =["list_of_recipients"],\nsubtype="plain")
         ''')

        msg = await self.__preape_message(message)

        async with Connection(self.config) as session:
            await session.session.send_message(msg)



