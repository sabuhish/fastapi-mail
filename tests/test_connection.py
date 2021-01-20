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



