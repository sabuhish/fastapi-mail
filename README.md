
# Fastapi-mail


Fastapi with fastapi-mail simple lightweight mail system, sending mails and attachments(individual && bulk)


### Installation ###

```sh
 $ pip install fastapi-mail
```




### Email Send example 
#### (this based on sending emails with gmail account, if you want your customize your config see below the example)

##### Before you dive in make sure you have already created  App password for more information;
- [Gmail Account App Password](https://support.google.com/mail/answer/185833?hl=en)

```python

from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi_mail import FastMail
from starlette.background import BackgroundTask
from test_examples.templates import  html, backgorund_task,bulkmail
from fastapi import Header,File, Body,Query, UploadFile

from pydantic import BaseModel
app = FastAPI()



class EmailSchema(BaseModel):
    email: str



#test email standart sending mail 
@app.post("/email")
async def my_awesome_func_1(email: EmailSchema) -> JSONResponse:



    mail = FastMail("******@gmail.com","******",tls=True)

    await  mail.send_message(email.email,"Test email from fastapi-mail", html, text_format="html")

    return JSONResponse(status_code=200, content={"message": f"email has been sent {email.email} address"})


#this mail sending using starlettes background tasks, faster than the above one
@app.post("/emailbackground")
async def my_awesome_func_2(email: dict = Body(...)) -> JSONResponse:

    email  = email.get("email")
    mail = FastMail("******@gmail.com","******",tls=True)


    task = BackgroundTask(mail.send_message, email,"Test email from fastapi-mail with background task",backgorund_task,text_format="html")

    return JSONResponse(status_code=200, 
                        content={"message": f"email has been sent {email} address"}, 
                        background=task)


#this an example of sending bulk mails
@app.post("/bulkemail")
async def my_awesome_func_3(email1: str=Body(...,embed=True),email2: str=Body(...,embed=True)) -> JSONResponse:

    mail = FastMail("your_account@gmail.com","*********",tls=True)

   
    task = BackgroundTask(mail.send_message, [email1,email2],"Bulk mail from fastapi-mail with background task","Bulk mail Test",text_format="plain",bulk=True)

    return JSONResponse(status_code=200, content={"message": f"email has been sent to these {email1,email2} addresses"}, background=task)


#an example of sending bulk mails attaching files 
@app.post("/bulkfile")
async def my_awesome_func_4(file: UploadFile = File(...), file2: UploadFile = File(...)) -> JSONResponse:

    email = ["someaddress@gmail.com","address2@gmail.com"]
    mail = FastMail("your_account@gmail.com","*********",tls=True)
  

    task = BackgroundTask(mail.send_message, email,"Bulk mail from fastapi-mail with background task","Bulk mail Test",text_format="plain",bulk=True,file=[file,file2])

    return JSONResponse(status_code=200, content={"message": f"email has been sent to these {email} addresses"}, background=task)



# uvicorn test_examples.main:app --reload  --port 8001
```

# Contributing
Fell free to open issue and send pull request.
