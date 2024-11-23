import os

import pytest

from fastapi_mail.msg import MailMsg
from fastapi_mail.schemas import MessageSchema, MessageType, MultipartSubtypeEnum


def test_initialize():
    message = MessageSchema(
        subject="test subject",
        recipients=["uzezio22@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    assert message.subject == "test subject"


def test_recipients_properly_initialized():
    message = MessageSchema(
        subject="test subject", recipients=[], body="test", subtype=MessageType.plain
    )

    assert message.recipients == []


def test_sendto_properly_set():
    msg = MessageSchema(
        subject="subject",
        recipients=["somebody@here.com", "somebody2@here.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        reply_to=["replyto@example.com"],
        subtype=MessageType.plain,
    )

    assert len(msg.recipients) == 2
    assert len(msg.cc) == 1
    assert len(msg.bcc) == 1
    assert len(msg.reply_to) == 1


def test_plain_message():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    assert message.body == "test"


def test_charset():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    assert message.charset == "utf-8"


def test_message_str():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    assert isinstance(message.body) == str


def test_plain_message_with_attachments():
    directory = os.getcwd()
    attachement = directory + "/tests/txt_files/plain.txt"
    content = "This file contents some information."

    msg = MessageSchema(
        subject="testing",
        recipients=["to@example.com"],
        attachments=[attachement],
        body="test mail body",
        subtype=MessageType.plain,
    )

    with open(attachement, "w") as file:
        file.write(content)

    assert len(msg.attachments) == 1


def test_empty_subject_header():
    message = MessageSchema(
        subject="",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    assert len(message.subject) == 0


def test_bcc():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        bcc=["bcc@example.com"],
        subtype=MessageType.plain,
    )

    assert len(msg.bcc) == 1
    assert msg.bcc == ["bcc@example.com"]


def test_replyto():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        reply_to=["replyto@example.com"],
        subtype=MessageType.plain,
    )

    assert len(msg.reply_to) == 1
    assert msg.reply_to == ["replyto@example.com"]


def test_cc():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        cc=["cc@example.com"],
        subtype=MessageType.plain,
    )

    assert len(msg.cc) == 1
    assert msg.cc == ["cc@example.com"]


def test_multipart_subtype():
    message = MessageSchema(
        subject="test subject",
        recipients=["to@example.com"],
        body="test",
        subtype=MessageType.plain,
    )
    assert message.multipart_subtype == MultipartSubtypeEnum.mixed


def test_headers():
    message = MessageSchema(
        subject="test subject",
        recipients=["to@example.com"],
        headers={"foo": "bar"},
        subtype=MessageType.plain,
    )

    assert message.headers == {"foo": "bar"}


@pytest.mark.asyncio
async def test_msgid_header():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    msg = MailMsg(message)
    msg_object = await msg._message("test@example.com")
    assert msg_object["Message-ID"] is not None


@pytest.mark.asyncio
async def test_message_charset():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
    )

    msg = MailMsg(message)
    msg_object = await msg._message("test@example.com")
    assert msg_object._charset is not None
    assert msg_object._charset == "utf-8"


def test_message_with_alternative_body_but_wrong_multipart_subtype():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
        alternative_body="alternative",
    )
    assert message.alternative_body is None


def test_message_with_alternative_body():
    message = MessageSchema(
        subject="test subject",
        recipients=["test@gmail.com"],
        body="test",
        subtype=MessageType.plain,
        multipart_subtype=MultipartSubtypeEnum.alternative,
        alternative_body="alternative",
    )
    assert message.alternative_body == "alternative"
