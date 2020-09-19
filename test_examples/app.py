from fastapi import FastAPI, BackgroundTasks, UploadFile,  File
from starlette.responses import JSONResponse
from templates import  html, template,bulkmail
from schema import  EmailSchema
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig



conf = ConnectionConfig(
    MAIL_USERNAME = "sebuhi.sukurov.sh@gmail.com",
    MAIL_PASSWORD = "jjhuacxnagzjeijm",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False)


app = FastAPI()

#test email standart sending mail 
@app.post("/email")
async def awesome_fastapi_func_1(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        receipients=email.dict().get("email"),
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

        

#this mail sending using starlettes background tasks, faster than the above one
@app.post("/emailbackground")
async def awesome_fastapi_func_2(background_tasks: BackgroundTasks,email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi mail module",
        receipients=email.dict().get("email"),
        body="Simple background task ",
        )

    fm = FastMail(conf)
    
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})



#an example of sending bulk mails attaching files 
@app.post("/file")
async def awesome_fastapi_func_4(background_tasks: BackgroundTasks,file: UploadFile = File(...)) -> JSONResponse:



    
    message = MessageSchema(
            subject="Fastapi mail module",
            receipients=["sabuhi.shukurov@gmail.com"],
            body="Simple background task ",
            attachments=[file]
            )

    fm = FastMail(conf)
        
    background_tasks.add_task(fm.send_message,message)

    return JSONResponse(status_code=200, content={"message": "email has been sent"})




# uvicorn test_examples.main:app --reload  --port 8001