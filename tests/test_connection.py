import os
from unittest.mock import patch

import pytest

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    MultipartSubtypeEnum,
)
from fastapi_mail.connection import Connection
from fastapi_mail.errors import EmptyMessagesList, PydanticClassRequired

CONTENT = "This file contents some information."


@pytest.mark.asyncio
async def test_connection(mail_config):
    message = MessageSchema(
        subject="test subject",
        recipients=["test@example.com"],
        body="test",
        subtype=MessageType.plain,
    )
    conf = ConnectionConfig(**mail_config)

    fm = FastMail(conf)

    await fm.send_message(message)

    assert message.body == "test"
    assert message.subtype == MessageType.plain
    assert not message.template_body


@pytest.mark.asyncio
async def test_timeout(mail_config):
    conf = ConnectionConfig(**mail_config)
    assert conf.TIMEOUT == 60


@pytest.mark.asyncio
async def test_html_message(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = "testing"
    to = "to@example.com"
    msg = MessageSchema(
        subject=subject, recipients=[to], body="Test data", subtype=MessageType.plain
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail["To"] == f"{to.split('@')[0]} <{to}>"
        assert mail["From"] == sender
        assert mail["Subject"] == subject
        assert msg.subtype == MessageType.plain
    assert msg.body == "Test data"


@pytest.mark.asyncio
async def test_attachement_message(mail_config):
    directory = os.getcwd()
    text_file = directory + "/tests/txt_files/plain.txt"

    with open(text_file, "w") as file:
        file.write(CONTENT)

    subject = "testing"
    to = "to@example.com"
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        body="html test",
        subtype="plain",
        attachments=[text_file],
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)
        mail = outbox[0]

        assert len(outbox) == 1
        assert mail._payload[1].get_content_maintype() == "application"
        assert (
            mail._payload[1].__dict__.get("_headers")[0][1]
            == "application/octet-stream"
        )


@pytest.mark.asyncio
async def test_message_with_headers(mail_config):
    subject = "testing"
    to = "to@example.com"
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        headers={"foo": "bar"},
        subtype=MessageType.plain,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)
        mail = outbox[0]
        assert ("foo", "bar") in mail._headers


@pytest.mark.asyncio
async def test_attachement_message_with_headers(mail_config):
    directory = os.getcwd()
    text_file = directory + "/tests/txt_files/plain.txt"

    with open(text_file, "w") as file:
        file.write(CONTENT)

    subject = "testing"
    to = "to@example.com"
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        body="Test data",
        subtype=MessageType.html,
        attachments=[
            {
                "file": text_file,
                "headers": {
                    "Content-ID": "test ID",
                    "Content-Disposition": 'inline; filename="plain.txt"',
                },
                "mime_type": "image",
                "mime_subtype": "png",
            },
            {
                "file": text_file,
                "mime_type": "image",
                "mime_subtype": "png",
            },
        ],
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail._payload[1].get_content_maintype() == msg.attachments[0][1].get(
            "mime_type"
        )
        assert mail._payload[1].get_content_subtype() == msg.attachments[0][1].get(
            "mime_subtype"
        )

        assert mail._payload[1].__dict__.get("_headers")[0][1] == "image/png"
        assert mail._payload[1].__dict__.get("_headers")[3][1] == msg.attachments[0][
            1
        ].get("headers").get("Content-ID")
        assert mail._payload[1].__dict__.get("_headers")[4][1] == msg.attachments[0][
            1
        ].get("headers").get("Content-Disposition")

        assert (
            mail._payload[2].__dict__.get("_headers")[3][1] == "attachment; "
            "filename*=UTF8''plain.txt"
        )


@pytest.mark.asyncio
async def test_jinja_message_list(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = "testing"
    to = "to@example.com"
    persons = [{"name": "Andrej"}]
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        template_body=persons,
        subtype=MessageType.html,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(
            message=msg, template_name="array_iteration_jinja_template.html"
        )

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail["To"] == f"{to.split('@')[0]} <{to}>"
        assert mail["From"] == sender
        assert mail["Subject"] == subject
    assert msg.subtype == MessageType.html
    assert msg.template_body == ("\n    \n    \n        Andrej\n    \n\n")


@pytest.mark.asyncio
async def test_jinja_message_dict(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = "testing"
    to = "to@example.com"
    persons = {"name": "Andrej"}

    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        template_body=persons,
        subtype=MessageType.html,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg, template_name="simple_jinja_template.html")

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail["To"] == f"{to.split('@')[0]} <{to}>"
        assert mail["From"] == sender
        assert mail["Subject"] == subject
    assert msg.subtype == MessageType.html
    assert msg.template_body == ("\n   Andrej\n")


@pytest.mark.asyncio
async def test_send_msg(mail_config):
    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        body="Test data",
        subtype=MessageType.html,
    )

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        assert outbox[0]["subject"] == "testing"
        assert outbox[0]["from"] == sender
        assert outbox[0]["To"] == "to <to@example.com>"


@pytest.mark.asyncio
async def test_send_msg_with_subtype(mail_config):
    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        body="<p> Test data </p>",
        subtype=MessageType.html,
    )

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        assert outbox[0]["subject"] == "testing"
        assert outbox[0]["from"] == sender
        assert outbox[0]["To"] == "to <to@example.com>"
    assert msg.body == "<p> Test data </p>"
    assert msg.subtype == MessageType.html


@pytest.mark.asyncio
async def test_jinja_message_with_html(mail_config):
    persons = [
        {"name": "Andrej"},
    ]

    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        template_body=persons,
        subtype=MessageType.html,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    await fm.send_message(
        message=msg, template_name="array_iteration_jinja_template.html"
    )

    assert msg.template_body == ("\n    \n    \n        Andrej\n    \n\n")

    assert not msg.body


@pytest.mark.asyncio
async def test_send_msg_with_alternative_body(mail_config):
    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        body="<p> Test data </p>",
        subtype=MessageType.html,
        alternative_body="Test data",
        multipart_subtype=MultipartSubtypeEnum.alternative,
    )

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        mail = outbox[0]
        assert len(outbox) == 1
        body = mail._payload[0]
        assert len(body._payload) == 2
        assert body._headers[1][1] == 'multipart/alternative; charset="utf-8"'
        assert mail["subject"] == "testing"
        assert mail["from"] == sender
        assert mail["To"] == "to <to@example.com>"

        assert body._payload[0]._headers[0][1] == 'text/html; charset="utf-8"'
        assert body._payload[1]._headers[0][1] == 'text/plain; charset="utf-8"'
    assert msg.alternative_body == "Test data"
    assert msg.multipart_subtype == MultipartSubtypeEnum.alternative


@pytest.mark.asyncio
async def test_send_msg_with_alternative_body_and_attachements(mail_config):
    directory = os.getcwd()
    text_file = directory + "/tests/txt_files/plain.txt"

    with open(text_file, "w") as file:
        file.write(CONTENT)

    subject = "testing"
    to = "to@example.com"
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        body="html test",
        subtype="html",
        attachments=[text_file],
        alternative_body="plain test",
        multipart_subtype="alternative",
    )
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        mail = outbox[0]

        assert len(outbox) == 1
        body = mail._payload[0]
        assert len(body._payload) == 2
        assert body._headers[1][1] == 'multipart/alternative; charset="utf-8"'
        assert mail["subject"] == "testing"
        assert mail["from"] == sender
        assert mail["To"] == "to <to@example.com>"

        assert body._payload[0]._headers[0][1] == 'text/html; charset="utf-8"'
        assert body._payload[1]._headers[0][1] == 'text/plain; charset="utf-8"'

        assert mail._payload[1].get_content_maintype() == "application"

        assert (
            mail._payload[1].__dict__.get("_headers")[0][1]
            == "application/octet-stream"
        )


@pytest.mark.asyncio
async def test_local_hostname_resolving(mail_config):
    # Test if the sessions local_hostname is set to the mail server name
    # or the LOCAL_HOSTNAME from the config depending on the configuration.
    mail_server_name = "my.fake.domain.com"
    with patch("socket.getfqdn", return_value=mail_server_name):
        conf = ConnectionConfig(**mail_config)
        async with Connection(conf) as session:
            assert session.session.local_hostname == mail_server_name

        conf.LOCAL_HOSTNAME = "localhost"
        async with Connection(conf) as session:
            assert session.session.local_hostname == conf.LOCAL_HOSTNAME


@pytest.mark.asyncio
async def test_jinja_html_and_plain_message(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = "testing"
    to = "to@example.com"
    persons = {"name": "Andrej"}

    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        template_body=persons,
        subtype=MessageType.html,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(
            message=msg, html_template="html.jinja", plain_template="text.jinja"
        )

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail["To"] == f"{to.split('@')[0]} <{to}>"
        assert mail["From"] == sender
        assert mail["Subject"] == subject
    assert msg.subtype == MessageType.html
    assert msg.template_body == "<b>Andrej</b>"
    assert msg.alternative_body == "Andrej"


@pytest.mark.asyncio
async def test_jinja_plain_and_html_message(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = "testing"
    to = "to@example.com"
    persons = {"name": "Andrej"}

    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        template_body=persons,
        subtype=MessageType.plain,
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(
            message=msg, html_template="html.jinja", plain_template="text.jinja"
        )

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail["To"] == f"{to.split('@')[0]} <{to}>"
        assert mail["From"] == sender
        assert mail["Subject"] == subject
    assert msg.subtype == MessageType.plain
    assert msg.template_body == "Andrej"
    assert msg.alternative_body == "<b>Andrej</b>"


@pytest.mark.asyncio
async def test_send_messages_bulk(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
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
            subtype=MessageType.html,
        ),
        MessageSchema(
            subject="Test 3",
            recipients=["user3@example.com"],
            body="Body 3",
            subtype=MessageType.plain,
        ),
    ]

    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1

    with fm.record_messages() as outbox:
        await fm.send_messages(messages)

        assert len(outbox) == 3
        assert outbox[0]["subject"] == "Test 1"
        assert outbox[0]["from"] == sender
        assert outbox[0]["To"] == "user1 <user1@example.com>"

        assert outbox[1]["subject"] == "Test 2"
        assert outbox[1]["from"] == sender
        assert outbox[1]["To"] == "user2 <user2@example.com>"

        assert outbox[2]["subject"] == "Test 3"
        assert outbox[2]["from"] == sender
        assert outbox[2]["To"] == "user3 <user3@example.com>"


@pytest.mark.asyncio
async def test_send_messages_empty_list(mail_config):
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with pytest.raises(EmptyMessagesList, match="Messages list is empty"):
        await fm.send_messages([])


@pytest.mark.asyncio
async def test_send_messages_invalid_type(mail_config):
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with pytest.raises(ValueError, match="messages must be a list"):
        await fm.send_messages("not-a-list")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_send_messages_invalid_message_type(mail_config):
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with pytest.raises(PydanticClassRequired):
        await fm.send_messages(["not-a-message"])  # type: ignore[list-item]


@pytest.mark.asyncio
async def test_send_messages_with_template(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    messages = [
        MessageSchema(
            subject="Greeting",
            recipients=["user1@example.com"],
            template_body={"name": "Alice"},
            subtype=MessageType.html,
        ),
        MessageSchema(
            subject="Greeting",
            recipients=["user2@example.com"],
            template_body={"name": "Bob"},
            subtype=MessageType.html,
        ),
    ]

    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1

    with fm.record_messages() as outbox:
        await fm.send_messages(messages, template_name="simple_jinja_template.html")

        assert len(outbox) == 2
        assert outbox[0]["from"] == sender
        assert outbox[1]["from"] == sender
        # templated body gets rendered into message payload
        alice_payload = outbox[0].get_payload()[0].get_payload(decode=True).decode()
        bob_payload = outbox[1].get_payload()[0].get_payload(decode=True).decode()
        assert "Alice" in alice_payload
        assert "Bob" in bob_payload

    assert messages[0].template_body == ("\n   Alice\n")
    assert messages[1].template_body == ("\n   Bob\n")


@pytest.mark.asyncio
async def test_send_messages_with_attachments(mail_config):
    directory = os.getcwd()
    text_file = directory + "/tests/txt_files/plain.txt"

    with open(text_file, "w") as file:
        file.write(CONTENT)

    messages = [
        MessageSchema(
            subject="Attachment 1",
            recipients=["user1@example.com"],
            body="Body 1",
            subtype=MessageType.plain,
            attachments=[text_file],
        ),
        MessageSchema(
            subject="Attachment 2",
            recipients=["user2@example.com"],
            body="Body 2",
            subtype=MessageType.plain,
            attachments=[text_file],
        ),
    ]

    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1

    with fm.record_messages() as outbox:
        await fm.send_messages(messages)

        assert len(outbox) == 2
        assert outbox[0]._payload[1].get_content_maintype() == "application"
        assert outbox[1]._payload[1].get_content_maintype() == "application"
