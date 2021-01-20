from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form
from starlette.responses import JSONResponse
from .templates import  html, template,bulkmail
from .schema import  EmailSchema, EmailStr
from starlette.requests import Request
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig


conf = ConnectionConfig(
    MAIL_USERNAME = "your_username",
    MAIL_PASSWORD = "strong_password",
    MAIL_FROM = "your@email.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "your mail server",
    MAIL_TLS = True,
    MAIL_SSL = False
    )

app = FastAPI()

#test email standart sending mail 
@app.post("/email")
async def simple_send(email: EmailSchema) -> JSONResponse:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=email.dict().get("email"),
        body=html,
        subtype="html"
        )

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

        

#this mail sending using starlettes background tasks, faster than the above one
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



#an example of sending attachments
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

