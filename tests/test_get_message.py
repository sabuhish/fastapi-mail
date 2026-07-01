import pytest

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType


@pytest.mark.asyncio
async def test_get_message_returns_prepared_message_without_sending(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        body="Test data",
        subtype=MessageType.plain,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        prepared = await fm.get_message(msg)

        # get_message prepares the message but must NOT dispatch/send it
        assert len(outbox) == 0

    assert not isinstance(prepared, list)
    assert prepared["Subject"] == "testing"
    assert prepared["From"] == sender
    assert prepared["To"] == "to <to@example.com>"
    body = prepared.get_payload()[0].get_payload(decode=True).decode()
    assert body == "Test data"


@pytest.mark.asyncio
async def test_get_message_bulk_returns_list(mail_config):
    messages = [
        MessageSchema(
            subject="Test 1",
            recipients=["user1@example.com"],
            body="Body 1",
            subtype=MessageType.plain,
        ),
        MessageSchema(
            subject="Test 2",
            recipients=["user2@example.com"],
            body="Body 2",
            subtype=MessageType.plain,
        ),
    ]
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    prepared = await fm.get_message(messages)

    assert isinstance(prepared, list)
    assert len(prepared) == 2
    assert prepared[0]["Subject"] == "Test 1"
    assert prepared[1]["Subject"] == "Test 2"


@pytest.mark.asyncio
async def test_get_message_with_template(mail_config):
    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        template_body={"name": "Andrej"},
        subtype=MessageType.html,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    prepared = await fm.get_message(msg, template_name="simple_jinja_template.html")

    assert not isinstance(prepared, list)
    assert prepared["Subject"] == "testing"
    rendered = prepared.get_payload()[0].get_payload(decode=True).decode()
    assert "Andrej" in rendered
