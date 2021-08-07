
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

---
**Documentation**: [FastApi-MAIL](https://sabuhish.github.io/fastapi-mail/)
---


The key features are:

-  sending emails with either with FastApi or using asyncio module 
-  sending emails using FastApi background task managment
-  sending files either from form-data or files from server
-  Using Jinja2 HTML Templates
-  email utils (utility allows you to check temporary email addresses, you can block any email or domain)
-  email utils has two available classes ```DefaultChecker``` and  ```WhoIsXmlApi```
-  Unittests using FastapiMail

More information on [Getting-Started](https://sabuhish.github.io/fastapi-mail/getting-started.html)


### Guide


```python

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import BaseModel, EmailStr
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
    MAIL_SSL = False,
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
        recipients=email.dict().get("email"),  # List of recipients, as many as you can pass 
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})     
```

## List of Examples

For more examples of using fastapi-mail please check [example](https://sabuhish.github.io/fastapi-mail/example/) section

# Contributing
Feel free to open issues and send pull requests.


## Contributors ✨

Thanks goes to these wonderful people ([🚧](https://sabuhish.github.io/fastapi-mail/example.html)):


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
    <td align="center"><a href=https://github.com/DmitriySolodkiy"><img src="https://avatars1.githubusercontent.com/u/37667152" width="100px;" alt=""/><br/><sub><b>Dmitriy Solodkiy</b></sub></a><br /><a href="#maintenance-tbenning" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/pboers1988"><img src="https://avatars1.githubusercontent.com/u/3235585" width="100px;" alt=""/><br /><sub><b>Peter Boers</b></sub></a><br /><a href="#maintenance-tbenning" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/jdvalentine"><img src="https://avatars.githubusercontent.com/u/557514" width="100px;" alt=""/><br /><sub><b>James Valentine</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a  href="#maintenance-jakebolam"  title="Maintenance">🚧</a> <a href="#tool-jfmengels" title="Tools">🔧</a></td>
    <td align="center"><a href="https://github.com/gogoku"><img src="https://avatars.githubusercontent.com/u/25707104" width="100px;" alt=""/><br /><sub><b>Gogoku</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a  href="#maintenance-jakebolam"  title="Maintenance">🚧</a> <a href="#tool-jfmengels" title="Tools">🔧</a></td>
    <td align="center"><a href="https://github.com/kucera-lukas"><img src="https://avatars.githubusercontent.com/u/85391931" width="100px;" alt=""/><br /><sub><b>Kucera-Lukas</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a  href="#maintenance-jakebolam"  title="Maintenance">🚧</a> <a href="#tool-jfmengels" title="Tools">🔧</a></td>
    <td align="center"><a href="https://github.com/LLYX"><img src="https://avatars.githubusercontent.com/u/10430633" width="100px;" alt=""/><br /><sub><b>LLYX</b></sub></a><br /><a href="https://github.com/marlin-dev/fastapi-mail/" title="Documentation">📖</a> <a  href="#maintenance-jakebolam"  title="Maintenance">🚧</a> <a href="#tool-jfmengels" title="Tools">🔧</a></td></tr>
  
<tr>
    <td align="center"><a href="https://github.com/floodpants"><img src="https://avatars.githubusercontent.com/u/37890036?" width="100px;" alt=""/><br /><sub><b>floodpants</b></sub></a><br /><a href="#maintenance-tbenning" title="Maintenance">🚧</a></td>
</tr>
</table>


This project follows the [all-contributors](https://allcontributors.org) specification.
Contributions of any kind are welcome!

Before you start please read [CONTRIBUTING](https://github.com/sabuhish/fastapi-mail/blob/master/CONTRIBUTING.md)



## LICENSE

[MIT](LICENSE)
