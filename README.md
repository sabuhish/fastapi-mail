
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
uvicorn examples.main:app --reload  --port 8001

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

### Sending email as background task

```python
   
@app.post("/emailbackground")
async def send_in_background(background_tasks: BackgroundTasks,email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=email.dict().get("email"),
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
            recipients=[email],
            body="Simple background task ",
            attachments=[file]
            )

    fm = FastMail(conf)
        
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})



```

###  Using Jinja2 HTML Templates

The email folder must be present within your applications working directory.

In sending HTML emails, the CSS expected by mail servers -outlook, google, etc- must be inline CSS. Fastapi mail passes _"body"_ to the rendered template. In creating the template for emails the dynamic objects should be used with the assumption that the variable is named "_body_" and that it is a python dict.

check out jinja2 for more details 
https://jinja.palletsprojects.com/en/2.11.x/


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
    TEMPLATE_FOLDER='./email templates folder'
)


@app.post("/email")
async def send_with_template(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        body=email.dict().get("body"),
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_template.html") ##optional field template_name is the name of the html file(jinja template) to use from the email template folder
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


```

##  Guide for email utils

The utility allows you to check temporary email addresses, you can block any email or domain. 
You can connect Redis to save and check email addresses. If you do not provide a Redis configuration, 
then the utility will save it in the list or set by default.


### Check dispasoble email address

```python
from fastapi import FastAPI, Query, Body
from starlette.responses import JSONResponse
from pydantic import EmailStr
from typing import List
from fastapi_mail.email_utils import DefaultChecker
from fastapi import Depends


app = FastAPI()


async def default_checker():
    checker = DefaultChecker()  # you can pass source argument for your own email domains
    await checker.fetch_temp_email_domains() # require to fetch temporary email domains
    return checker


@app.get('/email/dispasoble')
async def simple_send(domain: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    if await checker.is_dispasoble(domain):
        return JSONResponse(status_code=400, content={'message': 'this is dispasoble domain'})
    ...

    return JSONResponse(status_code=200, content={'message': 'email has been sent'})

```

### Add dispasoble email address

```python
@app.post('/email/dispasoble')
async def add_disp_domain(domains: list = Body(...,embed=True), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    res = await checker.add_temp_domain(domains)

    return JSONResponse(status_code=200, content={'result': res})
```

### Add domain to blocked list

```python
@app.post('/email/blocked/domains')
async def block_domain(domain: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    await checker.blacklist_add_domain(domain)
    
    return JSONResponse(status_code=200, content={'message': f'{domain} added to blacklist'})
```

### Check domain blocked or not

```python
@app.get('/email/blocked/domains')
async def get_blocked_domain(domain: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    res = await checker.is_blocked_domain(domain)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Add email address to blocked list

```python
@app.post('/email/blocked/address')
async def block_address(email: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    await checker.blacklist_add_email(email)
    
    return JSONResponse(status_code=200, content={"result": True})
```

### Check email blocked or not

```python
@app.get('/email/blocked/address')
async def get_block_address(email: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    res = await checker.is_blocked_address(email)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Check MX record

```python
@app.get('/email/mx')
async def test_mx(email: EmailStr = Query(...),full_result: bool = Query(False) ,checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:
    
    domain = email.split("@")[-1]
    res = await checker.check_mx_record(domain,full_result)
    
    return JSONResponse(status_code=200, content=res)
```

### Remove email address from blocked list

```python
@app.delete('/email/blocked/address')
async def del_blocked_address(email: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    res = await checker.blacklist_rm_email(email)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Remove domain from blocked list

```python
@app.delete('/email/blocked/domains')
async def del_blocked_domain(domain: str = Query(...), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

    res = await checker.blacklist_rm_domain(domain)
    
    return JSONResponse(status_code=200, content={"result": res})
```

### Remove domain from temporary list

```python
@app.delete('/email/dispasoble')
async def del_disp_domain(domains: list = Body(...,embed=True), checker: DefaultChecker = Depends(default_checker)) -> JSONResponse:

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

### Writing unittests using Fastapi_Mail
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
    TEMPLATE_FOLDER='./email templates folder',

    # if no indicated SUPPRESS_SEND defaults to 0 (false) as below
    SUPPRESS_SEND=0
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
from application.py import fm

# make this setting available as a fixture through conftest.py if you plan on using pytest
fm.config.SUPPRESS_SEND = 1

with fm.record_messages() as outbox:
    response = app.test_client.get("/email")
    assert len(outbox) == 1
    assert outbox[0].subject == "Testing"
```


# Contributing
Fell free to open issue and send pull request.


## Contributors ✨

Thanks goes to these wonderful people ([🚧](https://allcontributors.org/docs/en/maintenance)):


<table>
  <tr>
    <td align="center"><a href="https://github.com/marlin-dev"><img src="https://avatars.githubusercontent.com/u/46589585?v=3" width="100px;" alt=""/><br /><sub><b>Sabuhi Shukurov</b></sub></a><br /><a href="#maintenance-tbenning" title="Answering Questions">💬</a> <a href="https://github.com/marlin-dev/fastapi-mail/" title="Reviewed Pull Requests">👀</a> <a href="#maintenance-jakebolam" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/Turall"><img src="https://avatars.githubusercontent.com/u/32899328?v=3" width="100px;" alt=""/><br /><sub><b>Tural Muradov</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a href="https://github.com/marlin-dev/fastapi-mail/" title="Reviewed Pull Requests">👀</a> <a href="#tool-jfmengels" title="Tools">🔧</a></td>
    <td align="center"><a href="https://github.com/AliyevH"><img src="https://avatars.githubusercontent.com/u/5507950?v=3" width="100px;" alt=""/><br /><sub><b>Hasan Aliyev</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a href="#maintenance-jakebolam" title="Maintenance">🚧</a> <a href="https://github.com/marlin-dev/fastapi-mail/" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/imaskm"><img src="https://avatars.githubusercontent.com/u/20543833?v=3" width="100px;" alt=""/><br /><sub><b>Ashwani</b></sub></a><br /><a href="#maintenance-tbenning" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/LLYX"><img src="https://avatars1.githubusercontent.com/u/10430633" width="100px;" alt=""/><br /><sub><b>Leon Xu</b></sub></a><br /><a href="#maintenance-tbenning" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/gabrielponto"><img src="https://avatars.githubusercontent.com/u/7227328" width="100px;" alt=""/><br /><sub><b>Gabriel Oliveira</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a href="#maintenance-jakebolam" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/maestro-1"><img src="https://avatars0.githubusercontent.com/u/40833254" width="100px;" alt=""/><br /><sub><b>Onothoja Marho</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a  href="#maintenance-jakebolam"  title="Maintenance">🚧</a> <a href="#tool-jfmengels" title="Tools">🔧</a></td>

  </tr>
 <tr>
    <td align="center"><a href="https://github.com/TheTimKiely"><img src="https://avatars1.githubusercontent.com/u/34795732" width="100px;" alt=""/><br /><sub><b>Tim Kiely</b></sub></a><br /><a href="#maintenance-tbenning" title="Maintenance">🚧</a></td>

  </tr>
  

</table>


This project follows the [all-contributors](https://allcontributors.org) specification.
Contributions of any kind are welcome!

Before you start please read [CONTRIBUTING](https://github.com/sabuhish/fastapi-mail/blob/master/CONTRIBUTING.md)



## LICENSE

[MIT](LICENSE)