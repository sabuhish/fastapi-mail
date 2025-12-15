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

    assert isinstance(message.body, str)


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
    assert msg.bcc[0].email == "bcc@example.com"


def test_replyto():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        reply_to=["replyto@example.com"],
        subtype=MessageType.plain,
    )

    assert len(msg.reply_to) == 1
    assert msg.reply_to[0].email == "replyto@example.com"


def test_from_email():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        from_email="replyto@example.com",
        subtype=MessageType.plain,
    )

    assert msg.from_email == "replyto@example.com"


def test_from_name():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        from_name="No Reply",
        subtype=MessageType.plain,
    )

    assert msg.from_name == "No Reply"


def test_cc():
    msg = MessageSchema(
        subject="subject",
        recipients=[],
        cc=["cc@example.com"],
        subtype=MessageType.plain,
    )

    assert len(msg.cc) == 1
    assert msg.cc[0].email == "cc@example.com"


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


def test_name_email_recipients():
    """Test that recipients can accept NameEmail format"""
    message = MessageSchema(
        subject="test subject",
        recipients=["John Doe <john@example.com>"],
        body="test",
        subtype=MessageType.plain,
    )

    assert len(message.recipients) == 1
    assert message.recipients[0].name == "John Doe"
    assert message.recipients[0].email == "john@example.com"


def test_mixed_recipient_formats():
    """Test that recipients can accept both EmailStr and NameEmail formats"""
    message = MessageSchema(
        subject="test subject",
        recipients=["user@example.com", "Jane Smith <jane@example.com>"],
        body="test",
        subtype=MessageType.plain,
    )

    assert len(message.recipients) == 2
    assert message.recipients[0].name == "user"
    assert message.recipients[0].email == "user@example.com"
    assert message.recipients[1].name == "Jane Smith"
    assert message.recipients[1].email == "jane@example.com"


def test_name_email_cc_bcc_reply_to():
    """Test that cc, bcc, and reply_to can accept NameEmail format"""
    message = MessageSchema(
        subject="test subject",
        recipients=["test@example.com"],
        cc=["CC User <cc@example.com>"],
        bcc=["BCC User <bcc@example.com>"],
        reply_to=["Reply User <reply@example.com>"],
        body="test",
        subtype=MessageType.plain,
    )

    assert message.cc[0].name == "CC User"
    assert message.cc[0].email == "cc@example.com"
    assert message.bcc[0].name == "BCC User"
    assert message.bcc[0].email == "bcc@example.com"
    assert message.reply_to[0].name == "Reply User"
    assert message.reply_to[0].email == "reply@example.com"


@pytest.mark.asyncio
async def test_name_email_message_headers():
    """Test that NameEmail recipients are properly formatted in message headers"""
    message = MessageSchema(
        subject="test subject",
        recipients=["John Doe <john@example.com>", "Jane Smith <jane@example.com>"],
        cc=["CC User <cc@example.com>"],
        bcc=["BCC User <bcc@example.com>"],
        reply_to=["Reply User <reply@example.com>"],
        body="test",
        subtype=MessageType.plain,
    )

    msg = MailMsg(message)
    msg_object = await msg._message("sender@example.com")

    assert (
        msg_object["To"] == "John Doe <john@example.com>, Jane Smith <jane@example.com>"
    )
    assert msg_object["Cc"] == "CC User <cc@example.com>"
    assert msg_object["Bcc"] == "BCC User <bcc@example.com>"
    assert msg_object["Reply-To"] == "Reply User <reply@example.com>"
