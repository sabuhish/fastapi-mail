
from config import  ConnectionConfig
from errors import ConnectionErrors, PydanticClassRequired
from pydantic import BaseSettings  as Settings
import asyncio
import aiosmtplib






class Connection:
    '''
    Manages Connection to provided email service with its credentials
    '''

    def __init__(self,settings: Settings = ConnectionConfig):

        if not issubclass(settings,Settings):
            raise  PydanticClassRequired('''Email configuruation should be provided with Pydantic class, check example below:
         \nfrom pydantic import BaseSettings as Settings \nclass ConnectionConfig(Settings): \nMAIL_USERNAME:  EmailStr =None\nMAIL_PASSWORD: str =None \nMAIL_PORT: int  = 25 \nMAIL_SERVER: str = '127.0.0.1' \nMAIL_TLS: bool = False \nMAIL_SSL: bool = False \nconnection = Connection(ConnectionConfig)
         ''')

        self.settings = settings().__dict__


    async def __aenter__(self): #setting up a connection
        await self.__configure_connection()

    async def __aexit__(self, exc_type, exc, tb): #closing the connection
        await self.session.quit()


    async def __configure_connection(self):
        try:
            self.session =   aiosmtplib.SMTP(hostname=self.settings.get("MAIL_SERVER"), port=self.settings.get("MAIL_PORT"), use_tls=self.settings.get("MAIL_SSL"))          
            if self.settings.get("MAIL_TLS"):
                await self.session.starttls()
            
            await self.session.connect()

            await self.session.login(self.settings.get("MAIL_USERNAME"), self.settings.get("MAIL_PASSWORD"))

            return self.session

        except Exception as error:
            raise ConnectionErrors(f"Exception raised {error}, check your credentials or email service configuration") 




async def help():
    async with Connection() as conn:
        print("hello world")



asyncio.run(help())


