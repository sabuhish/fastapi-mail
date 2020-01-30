
# Fastapi-mail

The fastapi-mail simple lightweight mail system, sending emails and attachments(individual && bulk)


### Installation ###

```sh
 $ pip install fastapi-mail
```



## notes
- [The examples below based on gmail configuration, please read documentation for more information](https://support.google.com/mail/answer/185833?hl=en)
- if you want to use your custom mail server, see the latest example below

### In order to run the application use command below ####

```sh
uvicorn test_examples.main:app --reload  --port 8001

```

### Standart email sending example


```python

from fastapi import FastAPI, BackgroundTasks
from starlette.responses import JSONResponse
from fastapi_mail import FastMail
from fastapi import Header,File, Body,Query, UploadFile
from test_examples.schema import  EmailSchema
from pydantic import BaseModel,EmailStr

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


class EmailSchema(BaseModel):
    email: EmailStr



@app.post("/email")
async def awesome_fastapi_func_1(email: EmailSchema) -> JSONResponse:
    #as gmail requires TLS connection, therefore you require to set tls to True
    mail = FastMail(email="your_account@gmail.com",password="your_pass",tls=True,port="587",service="gmail")

    await  mail.send_message(recipient=email.email,subject="Test email from fastapi-mail", body=html, text_format="html")
    
    return JSONResponse(status_code=200, content={"message": f"email has been sent {email.email} address"})

        

```

### Sending email as background task

```python
   
@app.post("/emailbackground")
async def awesome_fastapi_func_2(background_tasks: BackgroundTasks,email: str = Body(...,embed=True)) -> JSONResponse:

    #this mail sending using fastapi background tasks, faster than the above one
    #Using Postman you can send post request, adding email in the body

    {
        "email": "recipient@gmail.com"
    }

    #for more information about background-tasks see the link below
    #https://fastapi.tiangolo.com/tutorial/background-tasks/

    mail = FastMail(email="your_account@gmail.com",password="your_pass",tls=True,port="587",service="gmail")


    background_tasks.add_task(mail.send_message, recipient=email,subject="testing HTML",body=template,text_format="html")
    

    return JSONResponse(status_code=200, 
                        content={"message": f"email has been sent {email} address"})

```


### Sending bulk mail 

```python


@app.post("/bulkemail")
async def awesome_fastapi_func_3(background_tasks: BackgroundTasks,emails: str=Body(...,embed=True)) -> JSONResponse:
    
   #this an example of sending bulk emails 
   ##Using Postman you can send post request, adding email in the body #example below
    {
        "emails": ["recipient1@gmail.com","recipient2@gmail.com"]
    }
    mail = FastMail(email="your_account@gmail.com",password="your_pass",tls=True,port="587",service="gmail")

    background_tasks.add_task(mail.send_message,recipient=[email1,email2],subject="Bulk mail from fastapi-mail with background task",body="Bulk mail Test",text_format="plain",bulk=True)


    return JSONResponse(status_code=200, content={"message": f"email has been sent to these {email1,email2} addresses"})


```

### Sending bulk mails && files


```python

@app.post("/bulkfile")
async def awesome_fastapi_func_4(background_tasks: BackgroundTasks,request: Request) -> JSONResponse:
    
    #this example of sending bulk email and sending multiple files
    mail = FastMail(email="your_account@gmail.com",password="your_pass",tls=True,port="587",service="gmail")

    temp = await  request.form()
    files= []

    for  value in temp.values():
        files.append(value)
 

    email = ["account_1@gmail.com","account_2@gmail.com"]
    mail = FastMail("******@gmail.com","******",tls=True)
    
    background_tasks.add_task(mail.send_message, recipient=email,subject="Bulk mail from fastapi-mail with background task",body="Bulk mail Test",text_format="plain",bulk=True,file=files)


    return JSONResponse(status_code=200, content={"message": f"email has been sent to these {email} addresses"})


```


### Custom  Mail server example ###

```python


@app.post("/custom")
async def awesome_fastapi_func_5(email: EmailSchema) -> JSONResponse:
    #In order to use custom mail service, you require to send services as keyword, and argument your mail server name. You must provide other information according to your mail server
    mail = FastMail(email="your_account@gmail.com",password="your_pass",tls=True,ssl=True,port="465",custom=True,services="info.v1.example.com")

    await  mail.send_message(recipient=email.email,subject="Test email from fastapi-mail", body=html, text_format="html")
    
    return JSONResponse(status_code=200, content={"message": f"email has been sent {email.email} address"})

```

# Contributing
Fell free to open issue and send pull request.
