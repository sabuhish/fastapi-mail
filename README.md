
# Fastapi-mail

The fastapi-mail simple lightweight mail system, sending emails and attachments(individual && bulk)


[![MIT licensed](https://img.shields.io/github/license/marlin-dev/fastapi-mail)](https://raw.githubusercontent.com/marlin-dev/fastapi-mail/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/marlin-dev/fastapi-mail.svg)](https://github.com/marlin-dev/fastapi-mail/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/marlin-dev/fastapi-mail.svg)](https://github.com/marlin-dev/fastapi-mail/network)
[![GitHub issues](https://img.shields.io/github/issues-raw/marlin-dev/fastapi-mail)](https://github.com/marlin-dev/fastapi-mail/issues)
[![Downloads](https://pepy.tech/badge/fastapi-mail)](https://pepy.tech/project/fastapi-mail)


###  🔨  Installation ###

```sh
 $ pip install fastapi-mail
```


### In order to run the application use command below ####

```sh
uvicorn test_examples.main:app --reload  --port 8001

```

### Guide


```python

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import EmailStr
from pydantic import EmailStr, BaseModel
from typing import List



class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = "your@email.com",
    MAIL_PASSWORD = "strong_password",
    MAIL_PORT = 587,
    MAIL_SERVER = "your mail server",
    MAIL_TLS = True,
    MAIL_SSL = False
)

app = FastAPI()


html = """
<html> 
<body>
<p>Hi This test mail
<br>Thanks for using Fastapi-mail</p> 
</body> 
</html>
"""

template = """
<html> 
<body>
<p>Hi This test mail using BackgroundTasks
<br>Thanks for using Fastapi-mail</p> 
</body> 
</html>
"""


@app.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        receipients=email.dict().get("email"),  # List of receipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
        

```

### Sending email as background task

```python
   
@app.post("/emailbackground")
async def send_in_background(background_tasks: BackgroundTasks,email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi mail module",
        receipients=email.dict().get("email"),
        body="Simple background task ",
        )

    fm = FastMail(conf)
    
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})


```


### Sending files


```python

@app.post("/file")
async def send_file(background_tasks: BackgroundTasks,file: UploadFile = File(...),email:EmailStr = Form(...)) -> JSONResponse:

    message = MessageSchema(
            subject="Fastapi mail module",
            receipients=[email],
            body="Simple background task ",
            attachments=[file]
            )

    fm = FastMail(conf)
        
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})



```


# Contributing
Fell free to open issue and send pull request. -->
