import pytest
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


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

    assert message.body == 'test'
    assert message.subtype == 'plain'
    assert not message.template_body
    assert not message.html


@pytest.mark.asyncio
async def test_html_message(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = 'testing'
    to = "to@example.com"
    msg = MessageSchema(subject=subject,
                        recipients=[to],
                        html="html test")
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail['To'] == to
        assert mail['From'] == sender
        assert mail['Subject'] == subject
        assert not msg.subtype
    assert msg.html == 'html test'


@pytest.mark.asyncio
async def test_jinja_message(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = 'testing'
    to = "to@example.com"
    persons = [
        {"name": "Andrej"},
        {"name": "Mark"},
        {"name": "Thomas"},
        {"name": "Lucy", },
        {"name": "Robert"},
        {"name": "Dragomir"}
    ]
    msg = MessageSchema(subject=subject,
                        recipients=[to],
                        template_body=persons)
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg, template_name='email.html')

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail['To'] == to
        assert mail['From'] == sender
        assert mail['Subject'] == subject
    assert msg.subtype == 'html'
    assert msg.template_body == '\n<p>\n    \n    Andrej\n\n    Mark\n\n    Thomas\n\n    Lucy\n\n    Robert\n\n    Dragomir\n\n</p>\n'


@pytest.mark.asyncio
async def test_send_msg(mail_config):
    msg = MessageSchema(subject="testing",
                        recipients=["to@example.com"],
                        body="html test")

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        assert outbox[0]["subject"] == "testing"
        assert outbox[0]["from"] == sender
        assert outbox[0]["To"] == "to@example.com"


@pytest.mark.asyncio
async def test_send_msg_with_subtype(mail_config):
    msg = MessageSchema(subject="testing",
                        recipients=["to@example.com"],
                        body="<p html test </p>",
                        subtype='html')

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        assert outbox[0]["subject"] == "testing"
        assert outbox[0]["from"] == sender
        assert outbox[0]["To"] == "to@example.com"
    assert msg.body == "<p html test </p>"
    assert msg.subtype == 'html'


@pytest.mark.asyncio
async def test_jinja_message_with_html(mail_config):
    persons = [
        {"name": "Andrej"},
        {"name": "Mark"},
        {"name": "Thomas"},
        {"name": "Lucy", },
        {"name": "Robert"},
        {"name": "Dragomir"}
    ]

    msg = MessageSchema(subject="testing",
                        recipients=["to@example.com"],
                        template_body=persons,
                        html='test html')
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with pytest.raises(ValueError):
        await fm.send_message(message=msg, template_name="email.html")
    assert msg.template_body == persons
    assert not msg.body
