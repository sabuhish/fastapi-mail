import os
import pytest
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig

@pytest.mark.asyncio
async def test_connection(mail_config):
    message = MessageSchema(
        subject="test subject",
        recipients=["sabuhi.shukurov@gmail.com"],
        body="test",
        subtype="plain"
    )
    conf = ConnectionConfig(**mail_config)

    fm = FastMail(conf)

    await fm.send_message(message)


    

@pytest.mark.asyncio
async def test_html_message(mail_config):
    
    directory = os.getcwd()
    html  = directory + "/files"
    
    msg = MessageSchema(subject="testing",
                        recipients=["to@example.com"],
                        
                        body="html test")
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    await fm.send_message(message=msg, template_name="test.html")

    assert msg.subtype == "html"

@pytest.mark.asyncio
async def test_html_message_with_body(mail_config):
    persons = [
        {'name': 'Andrej'}, 
        {'name': 'Mark' }, 
        {'name': 'Thomas'}, 
        {'name': 'Lucy', }, 
        {'name': 'Robert'}, 
        {'name': 'Dragomir'}
    ]

    directory = os.getcwd()
    html  = directory + "/files"
    
    msg = MessageSchema(subject="testing",
                        recipients=["to@example.com"],
                        body=persons)
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    await fm.send_message(message=msg, template_name="email.html")
    assert msg.body == '''
<p>
    
    Andrej

    Mark

    Thomas

    Lucy

    Robert

    Dragomir

</p>
'''


@pytest.mark.asyncio
async def test_html_message_with_html(mail_config):
    persons = [
        {'name': 'Andrej'}, 
        {'name': 'Mark' }, 
        {'name': 'Thomas'}, 
        {'name': 'Lucy', }, 
        {'name': 'Robert'}, 
        {'name': 'Dragomir'}
    ]

    directory = os.getcwd()
    html  = directory + "/files"
    
    msg = MessageSchema(subject="testing",
                        recipients=["to@example.com"],
                        html=persons)
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    await fm.send_message(message=msg, template_name="email.html")
    assert msg.html == '''
<p>
    
    Andrej

    Mark

    Thomas

    Lucy

    Robert

    Dragomir

</p>
'''