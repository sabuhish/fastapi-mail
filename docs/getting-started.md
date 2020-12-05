### 🕹 Guide

After installing the module you setup your `FastApi` app:

Main classes and packages are
```FastMail``` ```ConnectionConfig``` ```MessageSchema``` ```email_utils.DefaultChecker``` ```email_utils.WhoIsXmlApi```


### ```FastMail``` class
class has following attributes and methods

-  config  : ConnectionConfig class should be passed in order to establish connection

- send_message : The methods has two atributes, message: MessageSchema, template_name=None
    message : where you define message sturcture for email, if you are using jinja2 consider template_name as well for passing HTML.





### ```ConnectionConfig``` class
class has following attributes

-  MAIL_USERNAME  : Username for email, some email hosts separates username from the default sender(AWS).If you service does not provide username use sender address for connection.
-  MAIL_PASSWORD : Password for authentication
-  MAIL_SERVER  : SMTP Mail server.
-  MAIL_TLS : For TLS connection
-  MAIL_SSL : For TLS connection
-  MAIL_DEBUG : Debug mode for while sending mails, defaults 0.
-  MAIL_FROM : Sender address
-  MAIL_FROM_NAME : Title for Mail
-  TEMPLATE_FOLDER: If you are using jinja2, specify template folder name
-  SUPPRESS_SEND:  To mock sending out mail, defaults 0.



### ```MessageSchema``` class
class has following attributes and methods



### ```email_utils.DefaultChecker``` class
class has following attributes and methods

-  config  : ConnectionConfig class should be passed in order to establish connection

- send_message : The methods has two atributes, message: MessageSchema, template_name=None
    message : where you define message sturcture for email, if you are using jinja2 consider template_name as well for passing HTML.




### ```email_utils.WhoIsXmlApi``` class
class has following attributes and methods

-  config  : ConnectionConfig class should be passed in order to establish connection

- send_message : The methods has two atributes, message: MessageSchema, template_name=None
    message : where you define message sturcture for email, if you are using jinja2 consider template_name as well for passing HTML.



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
    MAIL_USERNAME = "YourUsername",
    MAIL_PASSWORD = "strong_password",
    MAIL_FROM = "your@email.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "your mail server",
    MAIL_TLS = True,
    MAIL_SSL = False
)

app = FastAPI()


html = """
<p>Hi this test mail, thanks for using Fastapi-mail</p> 
"""

template = """
<p>Hi this test mail using BackgroundTasks, thanks for using Fastapi-mail</p> 
"""


@app.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
```


```python



