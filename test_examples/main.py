from fastapi import FastAPI, BackgroundTasks
from starlette.responses import JSONResponse
from fastapi_mail import FastMail
from test_examples.templates import  html, template,bulkmail
from fastapi import Header,File, Body,Query, UploadFile
from test_examples.schema import  EmailSchema
from typing import List
from starlette.requests import Request

app = FastAPI()



      # service = SendMail("sebuhi.sukurov.sh@gmail.com","jjhuacxnagzjeijm")


#test email standart sending mail 
@app.post("/email")
async def awesome_fastapi_func_1(email: EmailSchema) -> JSONResponse:

    mail = FastMail("******@gmail.com","******",tls=True)

    await  mail.send_message(recipient=email.email,subject="Test email from fastapi-mail", body=html, text_format="html")
    
    return JSONResponse(status_code=200, content={"message": f"email has been sent {email.email} address"})

        

#this mail sending using starlettes background tasks, faster than the above one
@app.post("/emailbackground")
async def awesome_fastapi_func_2(background_tasks: BackgroundTasks,email: str = Body(...,embed=True)) -> JSONResponse:

    mail = FastMail("******@gmail.com","******",tls=True)

    background_tasks.add_task(mail.send_message, recipient=email,subject="testing HTML",body=template,text_format="html")

    return JSONResponse(status_code=200, 
                        content={"message": f"email has been sent {email} address"})


#this an example of sending bulk mails
@app.post("/bulkemail")
async def awesome_fastapi_func_3(background_tasks: BackgroundTasks,emails: list=Body(...,embed=True)) -> JSONResponse:

    mail = FastMail("your_account@gmail.com","*********",tls=True)

   
    background_tasks.add_task(mail.send_message,recipient=[email1,email2],subject="Bulk mail from fastapi-mail with background task",body="Bulk mail Test",text_format="plain",bulk=True)

    
    return JSONResponse(status_code=200, content={"message": f"email has been sent to these {email1,email2} addresses"})



#an example of sending bulk mails attaching files 
@app.post("/bulkfile")
async def awesome_fastapi_func_4(background_tasks: BackgroundTasks,request: Request) -> JSONResponse:
    temp = await  request.form()

    files= []

    for  value in temp.values():
        files.append(value)
    
       # service = SendMail("sebuhi.sukurov.sh@gmail.com","jjhuacxnagzjeijm")

    email = ["sabuhi.shukurov@gmail.com","sabus02@gmail.com"]
    mail = FastMail("sebuhi.sukurov.sh@gmail.com","jjhuacxnagzjeijm",tls=True)
    
    background_tasks.add_task(mail.send_message, email,"Bulk mail from fastapi-mail with background task","Bulk mail Test",text_format="plain",bulk=True,file=files)


    return JSONResponse(status_code=200, content={"message": f"email has been sent to these {email} addresses"})




# uvicorn test_examples.main:app --reload  --port 8001