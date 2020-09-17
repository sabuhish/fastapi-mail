from fastapi import FastAPI
from fastapi_mail.fastmail import FastMail
from pydantic import BaseSettings
from pydantic import EmailStr


app = FastAPI()


class ProdSettings(BaseSettings):
    email = "info@offer.az"
    password = "jobs_2020"
    port = 465
    server = "cpanel1.v.fuzzy.com"
    text_format = "html"

settings = ProdSettings()


fastmail = FastMail(settings)






