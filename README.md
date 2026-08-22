
# Fastapi-mail

Simple lightweight mail system for FastAPI — send emails, attachments, and HTML templates.

[![MIT licensed](https://img.shields.io/github/license/sabuhish/fastapi-mail)](https://raw.githubusercontent.com/sabuhish/fastapi-mail/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/sabuhish/fastapi-mail.svg)](https://github.com/sabuhish/fastapi-mail/stargazers)
[![GitHub issues](https://img.shields.io/github/issues-raw/sabuhish/fastapi-mail)](https://github.com/sabuhish/fastapi-mail/issues)
[![Downloads](https://pepy.tech/badge/fastapi-mail)](https://pepy.tech/project/fastapi-mail)


**Documentation**: [sabuhish.github.io/fastapi-mail](https://sabuhish.github.io/fastapi-mail/)

---

### Installation

```bash
pip install fastapi-mail
```

### Quick Start

```python
from typing import List

from fastapi import FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType, NameEmail
from pydantic import BaseModel
from starlette.responses import JSONResponse


class EmailSchema(BaseModel):
    email: List[NameEmail]


conf = ConnectionConfig(
    MAIL_USERNAME="username",
    MAIL_PASSWORD="**********",
    MAIL_FROM="test@email.com",
    MAIL_PORT=465,
    MAIL_SERVER="mail server",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

app = FastAPI()


@app.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:
    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.model_dump().get("email"),
        body="<p>Thanks for using Fastapi-mail</p>",
        subtype=MessageType.html,
    )
    await FastMail(conf).send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
```

## Contributing

Contributions of any kind are welcome! Please read [CONTRIBUTING](https://github.com/sabuhish/fastapi-mail/blob/master/CONTRIBUTING.md) before you start.

## Contributors

Thanks goes to these wonderful [people](https://github.com/sabuhish/fastapi-mail/graphs/contributors).

## LICENSE

[MIT](LICENSE)
