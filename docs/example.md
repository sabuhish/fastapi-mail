

## Sending email with FastApi

### List of Useful Examples
```python
from fastapi import (
    FastAPI, 
    BackgroundTasks, 
    UploadFile, File, 
    Form, 
    Query,
    Body,
    Depends
)
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List
from fastapi_mail.email_utils import DefaultChecker

class EmailSchema(BaseModel):
    email: List[EmailStr]


conf = ConnectionConfig(
    MAIL_USERNAME = "YourUsername",
    MAIL_PASSWORD = "strong_password",
    MAIL_FROM = "your@email.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "your mail server",
    MAIL_FROM_NAME="Desired Name",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

app = FastAPI()


html = """
<p>Hi this test mail, thanks for using Fastapi-mail</p> 
"""


@app.post("/email")
async def simple_send(
    email: EmailSchema
    ) -> JSONResponse:

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

###  Email as background task

```python
   
@app.post("/emailbackground")
async def send_in_background(
    background_tasks: BackgroundTasks,
    email: EmailSchema
    ) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=email.dict().get("email"),
        body="Simple background task",
        )

    fm = FastMail(conf)
    
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})
```


### Sending files

```python

@app.post("/file")
async def send_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    email:EmailStr = Form(...)
    ) -> JSONResponse:

    message = MessageSchema(
            subject="Fastapi mail module",
            recipients=[email],
            body="Simple background task ",
            attachments=[file]
            )

    fm = FastMail(conf)
        
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})
```


### Using Jinja2 HTML Templates

You can enable Jinja2 HTML Template emails by setting the `TEMPLATE_FOLDER` configuration option, and supplying a 
value (which is just the name of the template file within the `TEMPLATE_FOLDER` dir) for the `template_name` parameter 
in `FastMail.send_message()`. You then can pass a Dict as the `template_body` property of your `MessageSchema` object:

```python

class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]

conf = ConnectionConfig(
    MAIL_USERNAME = "YourUsername",
    MAIL_PASSWORD = "strong_password",
    MAIL_FROM = "your@email.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "your mail server",
    MAIL_TLS = True,
    MAIL_SSL = False,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)


@app.post("/email")
async def send_with_template(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        template_body=email.dict().get("body"),
        )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_template.html") 
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


```

For example, assume we pass a `template_body` of:

```json
{
  "first_name": "Fred",
  "last_name": "Fredsson"
}
```

We can reference the variables in our Jinja templates as per normal:

```
...
<span>Hello, {{ first_name }}!</span>
...
```

#### Legacy Behaviour (<= 0.4.0)

The original behaviour in <= 0.4.0 was to wrap the Dict you provide in a variable named `body` when it was provided to 
Jinja behind the scenes. In these versions, you can then access your dict in your template like so:


```
...
<span>Hello,  body.first_name !</span>
...
```


As you can see our keys in our dict are no longer the top level, they are part of the `body` variable. Nesting works 
as per normal below this level also. 

### Customizing attachments by headers and MIME type

Used for example for referencing Content-ID images in html of email

```python
message = MessageSchema(
    subject='Fastapi-Mail module',
    recipients=recipients,
    html="<img src='cid:logo_image'>",
    subtype='html',
    attachments=[
            {
                "file": "/path/to/file.png"),
                "headers": {"Content-ID": "<logo_image>"},
                "mime_type": "image",
                "mime_subtype": "png",
            }
        ],
)

fm = FastMail(conf)
await fm.send_message(message)
```

### Adding custom SMTP headers
```python
message = MessageSchema(
    subject='Fastapi-Mail module',
    recipients=recipients,
    headers={"your custom header": "your custom value"}
)

fm = FastMail(conf)
await fm.send_message(message)
```

##  Guide for email utils

The utility allows you to check temporary email addresses, you can block any email or domain. 
You can connect Redis to save and check email addresses. If you do not provide a Redis configuration, 
then the utility will save it in the list or set by default.


### Check disposable email address

```python

async def default_checker():
    checker = DefaultChecker()  # you can pass source argument for your own email domains
    await checker.fetch_temp_email_domains() # require to fetch temporary email domains
    return checker


@app.get('/email/disposable')
async def simple_send(
    domain: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    if await checker.is_disposable(domain):
        return JSONResponse(status_code=400, content={'message': 'this is disposable domain'})

    return JSONResponse(status_code=200, content={'message': 'email has been sent'})

```

### Add disposable email address

```python
@app.post('/email/disposable')
async def add_disp_domain(
    domains: list = Body(...,embed=True), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    res = await checker.add_temp_domain(domains)

    return JSONResponse(status_code=200, content={'result': res})
```

### Add domain to blocked list

```python
@app.post('/email/blocked/domains')
async def block_domain(
    domain: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    await checker.blacklist_add_domain(domain)
    
    return JSONResponse(status_code=200, content={'message': f'{domain} added to blacklist'})
```

### Check domain blocked or not

```python
@app.get('/email/blocked/domains')
async def get_blocked_domain(
    domain: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    res = await checker.is_blocked_domain(domain)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Add email address to blocked list

```python
@app.post('/email/blocked/address')
async def block_address(
    email: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    await checker.blacklist_add_email(email)
    
    return JSONResponse(status_code=200, content={"result": True})
```

### Check email blocked or not

```python
@app.get('/email/blocked/address')
async def get_block_address(
    email: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    res = await checker.is_blocked_address(email)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Check MX record

```python
@app.get('/email/mx')
async def test_mx(
    email: EmailStr = Query(...),
    full_result: bool = Query(False) ,
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:
    
    domain = email.split("@")[-1]
    res = await checker.check_mx_record(domain,full_result)
    
    return JSONResponse(status_code=200, content=res)
```

### Remove email address from blocked list

```python
@app.delete('/email/blocked/address')
async def del_blocked_address(
    email: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    res = await checker.blacklist_rm_email(email)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Remove domain from blocked list

```python
@app.delete('/email/blocked/domains')
async def del_blocked_domain(
    domain: str = Query(...), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    res = await checker.blacklist_rm_domain(domain)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Remove domain from temporary list

```python
@app.delete('/email/disposable')
async def del_disp_domain(
    domains: list = Body(...,embed=True), 
    checker: DefaultChecker = Depends(default_checker)
    ) -> JSONResponse:

    res = await checker.blacklist_rm_temp(domains)

    return JSONResponse(status_code=200, content={'result': res})
```

### Use email utils with Redis

```python

async def default_checker():
    checker = DefaultChecker(db_provider="redis")
    await checker.init_redis()
    return checker

```
 
###  WhoIsXmlApi
```python
from email_utils import WhoIsXmlApi

who_is = WhoIsXmlApi(token="Your access token", email="your@mailaddress.com")

print(who_is.smtp_check_())    #check smtp server
print(who_is.is_disposable()) # check email is disposable or not
print(who_is.check_mx_record()) # check domain mx records 
print(who_is.free_check) # check email domain is free or not

```

## Unittests using FastapiMail
Fastapi mails allows you to write unittest for your application without sending emails to
non existent email address by mocking the email to be sent. To mock sending out mails, set
the suppress configuraton to true. Suppress send defaults to False to prevent mocking within applications.


application.py

```python
conf = ConnectionConfig(
    MAIL_USERNAME = "YourUsername",
    MAIL_PASSWORD = "strong_password",
    MAIL_FROM = "your@email.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "your mail server",
    MAIL_TLS = True,
    MAIL_SSL = False,
    TEMPLATE_FOLDER = Path(__file__).parent / 'templates',

    # if no indicated SUPPRESS_SEND defaults to 0 (false) as below
    # SUPPRESS_SEND=1
)

fm = FastMail(conf)

@app.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Testing",
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

```

test.py
```python
from starlette.testclient import TestClient
from .application import app, fm

client = TestClient(app)


def test_send_msg():
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        payload = {"email": [ "user@example.com"]}
        response = client.post("/email",json=payload)
        assert response.status_code == 200
        assert len(outbox) == 1
        assert outbox[0]['from'] == "your@email.com"
        assert outbox[0]['To'] == "user@example.com"

```

