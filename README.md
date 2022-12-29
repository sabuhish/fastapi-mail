
# Fastapi-mail

The fastapi-mail is a simple lightweight mail system, for sending emails and attachments(individual && bulk)


[![MIT licensed](https://img.shields.io/github/license/sabuhish/fastapi-mail)](https://raw.githubusercontent.com/sabuhish/fastapi-mail/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/sabuhish/fastapi-mail.svg)](https://github.com/sabuhish/fastapi-mail/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/sabuhish/fastapi-mail.svg)](https://github.com/sabuhish/fastapi-mail/network)
[![GitHub issues](https://img.shields.io/github/issues-raw/sabuhish/fastapi-mail)](https://github.com/sabuhish/fastapi-mail/issues)
[![Downloads](https://pepy.tech/badge/fastapi-mail)](https://pepy.tech/project/fastapi-mail)


###  🔨  Installation ###


```bash
python3 -m venv .venv

source .venv/bin/activate

pip install fastapi-mail

for aioredis and httpx

pip install 'fastapi-mail[aioredis]'
pip install 'fastapi-mail[httpx]'

```

Alternatively, if you prefer to use `poetry` for package dependencies:

```bash
poetry shell

poetry add fastapi-mail

for aioredis and httpx

poetry add 'fastapi-mail[aioredis]'
poetry add 'fastapi-mail[httpx]'
```

---
**Documentation**: [FastApi-MAIL](https://sabuhish.github.io/fastapi-mail/)
---


The key features are:

-  sending emails either with FastApi or using asyncio module 
-  sending emails using FastApi background task managment
-  sending files either from form-data or files from server
-  Using Jinja2 HTML Templates
-  email utils (utility allows you to check temporary email addresses, you can block any email or domain)
-  email utils has two available classes ```DefaultChecker``` and  ```WhoIsXmlApi```
-  Unittests using FastapiMail

More information on [Getting-Started](https://sabuhish.github.io/fastapi-mail/getting-started/)


### Guide


```python

from typing import List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse



class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME ="username",
    MAIL_PASSWORD = "**********",
    MAIL_FROM = "test@email.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "mail server",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

app = FastAPI()


html = """
<p>Thanks for using Fastapi-mail</p> 
"""


@app.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})     
```

## List of Examples

For more examples of using fastapi-mail please check: 
[example](https://sabuhish.github.io/fastapi-mail/example/) section.


## Contributors ✨

Thanks goes to these wonderful
[People](https://github.com/sabuhish/fastapi-mail/blob/master/contributors.txt)


# Contributing
Contributions of any kind are welcome!

Before you start, please read [CONTRIBUTING](https://github.com/sabuhish/fastapi-mail/blob/master/CONTRIBUTING.md)


## LICENSE

[MIT](LICENSE)
