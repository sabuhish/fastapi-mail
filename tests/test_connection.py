import os

import pytest

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

CONTENT = 'file test content'


@pytest.mark.asyncio
async def test_connection(mail_config):
    message = MessageSchema(
        subject='test subject',
        recipients=['sabuhi.shukurov@gmail.com'],
        body='test',
        subtype='plain',
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
    to = 'to@example.com'
    msg = MessageSchema(subject=subject, recipients=[to], html='html test')
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
async def test_attachement_message(mail_config):
    directory = os.getcwd()
    attachement = directory + '/files/attachement.txt'

    with open(attachement, 'w') as file:
        file.write(CONTENT)

    subject = 'testing'
    to = 'to@example.com'
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        html='html test',
        subtype='html',
        attachments=[attachement],
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)
        mail = outbox[0]

        assert len(outbox) == 1
        assert mail._payload[1].get_content_maintype() == 'application'
        assert mail._payload[1].__dict__.get('_headers')[0][1] == 'application/octet-stream'


@pytest.mark.asyncio
async def test_message_with_headers(mail_config):
    subject = 'testing'
    to = 'to@example.com'
    msg = MessageSchema(subject=subject, recipients=[to], headers={'foo': 'bar'})
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)
        mail = outbox[0]
        assert ('foo', 'bar') in mail._headers


@pytest.mark.asyncio
async def test_attachement_message_with_headers(mail_config):
    directory = os.getcwd()
    attachement = directory + '/files/attachement.txt'

    with open(attachement, 'w') as file:
        file.write(CONTENT)

    subject = 'testing'
    to = 'to@example.com'
    msg = MessageSchema(
        subject=subject,
        recipients=[to],
        html='html test',
        subtype='html',
        attachments=[
            {
                'file': attachement,
                'headers': {
                    'Content-ID': 'test ID',
                    'Content-Disposition': 'inline; filename="attachement.txt"',
                },
                'mime_type': 'image',
                'mime_subtype': 'png',
            },
            {
                'file': attachement,
                'mime_type': 'image',
                'mime_subtype': 'png',
            },
        ],
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail._payload[1].get_content_maintype() == msg.attachments[0][1].get('mime_type')
        assert mail._payload[1].get_content_subtype() == msg.attachments[0][1].get('mime_subtype')

        assert mail._payload[1].__dict__.get('_headers')[0][1] == 'image/png'
        assert mail._payload[1].__dict__.get('_headers')[3][1] == msg.attachments[0][1].get(
            'headers'
        ).get('Content-ID')
        assert mail._payload[1].__dict__.get('_headers')[4][1] == msg.attachments[0][1].get(
            'headers'
        ).get('Content-Disposition')

        assert (
            mail._payload[2].__dict__.get('_headers')[3][1] == 'attachment; '
            "filename*=UTF8''attachement.txt"
        )


@pytest.mark.asyncio
async def test_jinja_message_list(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = 'testing'
    to = 'to@example.com'
    persons = [
        {'name': 'Andrej'},
    ]
    msg = MessageSchema(subject=subject, recipients=[to], template_body=persons)
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
    assert msg.template_body == ('\n    \n    \n        Andrej\n    \n\n\n')


@pytest.mark.asyncio
async def test_jinja_message_dict(mail_config):
    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    subject = 'testing'
    to = 'to@example.com'
    persons = {'name': 'Andrej'}

    msg = MessageSchema(subject=subject, recipients=[to], template_body=persons)
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with fm.record_messages() as outbox:
        await fm.send_message(message=msg, template_name='email_dict.html')

        assert len(outbox) == 1
        mail = outbox[0]
        assert mail['To'] == to
        assert mail['From'] == sender
        assert mail['Subject'] == subject
    assert msg.subtype == 'html'
    assert msg.template_body == ('\n   Andrej\n\n')


@pytest.mark.asyncio
async def test_send_msg(mail_config):
    msg = MessageSchema(subject='testing', recipients=['to@example.com'], body='html test')

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        assert outbox[0]['subject'] == 'testing'
        assert outbox[0]['from'] == sender
        assert outbox[0]['To'] == 'to@example.com'


@pytest.mark.asyncio
async def test_send_msg_with_subtype(mail_config):
    msg = MessageSchema(
        subject='testing', recipients=['to@example.com'], body='<p html test </p>', subtype='html'
    )

    sender = f"{mail_config['MAIL_FROM_NAME']} <{mail_config['MAIL_FROM']}>"
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)
    fm.config.SUPPRESS_SEND = 1
    with fm.record_messages() as outbox:
        await fm.send_message(message=msg)

        assert len(outbox) == 1
        assert outbox[0]['subject'] == 'testing'
        assert outbox[0]['from'] == sender
        assert outbox[0]['To'] == 'to@example.com'
    assert msg.body == '<p html test </p>'
    assert msg.subtype == 'html'


@pytest.mark.asyncio
async def test_jinja_message_with_html(mail_config):
    persons = [
        {'name': 'Andrej'},
    ]

    msg = MessageSchema(
        subject='testing', recipients=['to@example.com'], template_body=persons, html='test html'
    )
    conf = ConnectionConfig(**mail_config)
    fm = FastMail(conf)

    with pytest.raises(ValueError):
        await fm.send_message(message=msg, template_name='email.html')

    assert msg.template_body == ('\n    \n    \n        Andrej\n    \n\n\n')

    assert not msg.body
