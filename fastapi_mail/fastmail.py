import aiosmtplib
from pydantic import BaseModel
from fastapi_mail.config import ConnectionConfig
from fastapi_mail.connection import Connection
from fastapi_mail.schemas import MessageSchema
from fastapi_mail.msg import MailMsg
from fastapi_mail.errors import PydanticClassRequired

class FastMail:
    '''
    Fastapi mail system sending mails(individual, bulk) attachments(individual, bulk)

    :param config: Connection config to be passed

    '''

    def __init__(self,
        config: ConnectionConfig
        ):

        self.config = config

    async def get_mail_template(self, env_path, template_name):
        template = env_path.get_template(template_name)
        return template

    async def __preape_message(self, message, template=None):
        if hasattr(message, "body") and template is not None:
            message.body = template.render(body=message.body)
            if hasattr(message, "subtype") and getattr(message, "subtype") != "html":
                message.subtype = "html"

        msg = MailMsg(**message.dict())
        if self.config.MAIL_FROM_NAME is not None:
            sender = f'{self.config.MAIL_FROM_NAME} {self.config.MAIL_FROM}'
        else:
            sender = self.config.MAIL_FROM
        return await msg._message(sender)

    async def send_message(self, message: MessageSchema, template_name=None):

        if not issubclass(message.__class__, BaseModel):
            raise PydanticClassRequired('''Message schema should be provided from MessageSchema class, check example below:
         \nfrom fastmail import MessageSchema  \nmessage = MessageSchema(\nsubject = "subject",\nrecipients= ["list_of_recipients"],\nbody = "Hello World",\ncc = ["list_of_recipients"],\nbcc =["list_of_recipients"],\nsubtype="plain")
         ''')

        if self.config.TEMPLATE_FOLDER and template_name:
            template = await self.get_mail_template(self.config.TEMPLATE_FOLDER, template_name)
            msg = await self.__preape_message(message, template)
        else:
            msg = await self.__preape_message(message)

        async with Connection(self.config) as session:
            await session.session.send_message(msg)
