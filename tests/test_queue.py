import pytest
from datetime import datetime, timedelta
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi_mail.queue import EmailQueue, EmailStatus
import asyncio

@pytest.fixture
def queued_message():
    return MessageSchema(
        subject="Test subject",
        recipients=["test@example.com"],
        body="Test email body",
        subtype=MessageType.plain
    )

@pytest.fixture
def queue_config(mail_config):
    mail_config["SUPPRESS_SEND"] = 1
    return ConnectionConfig(**mail_config)

@pytest.fixture
def email_queue(queue_config):
    fastmail = FastMail(queue_config)
    return EmailQueue(fastmail)

@pytest.mark.asyncio
async def test_add_to_queue(email_queue, queued_message):
    queue_id = await email_queue.add_to_queue(queued_message)
    assert queue_id in email_queue.queue
    assert email_queue.queue[queue_id].status.name == "QUEUED"
    assert email_queue.queue[queue_id].message == queued_message
    assert email_queue.queue[queue_id].retry_count == 0

@pytest.mark.asyncio
async def test_scheduled_email(email_queue, queued_message):
    schedule_time = datetime.now() + timedelta(hours=1)
    queue_id = await email_queue.add_to_queue(queued_message, schedule_time=schedule_time)
    queued_email = email_queue.queue[queue_id]
    assert queued_email.scheduled_time == schedule_time
    assert queued_email.status.name == "QUEUED"

@pytest.mark.asyncio
async def test_process_queue(email_queue, queued_message):
    queue_id = await email_queue.add_to_queue(queued_message)
    email_queue.start_processing()
    await asyncio.sleep(2)
    email_queue.stop_processing()
    processed_email = email_queue.queue[queue_id]
    assert processed_email.status.name == "SENT"

@pytest.mark.asyncio
async def test_queue_status(email_queue, queued_message):
    queue_id1 = await email_queue.add_to_queue(queued_message)
    queue_id2 = await email_queue.add_to_queue(queued_message)
    email_queue.queue[queue_id2].status = EmailStatus.FAILED
    email_queue.queue[queue_id2].retry_count = 3
    status = email_queue.get_queue_status()
    assert status["total"] == 2
    assert status["queued"] == 1
    assert status["failed"] == 1

@pytest.mark.asyncio
async def test_cancel_email(email_queue, queued_message):
    queue_id = await email_queue.add_to_queue(queued_message)
    success = email_queue.cancel_email(queue_id)
    assert success is True
    assert queue_id not in email_queue.queue
    assert email_queue.cancel_email("non-existent") is False

@pytest.mark.asyncio
async def test_retry_failed_email(email_queue, queued_message):
    queue_id = await email_queue.add_to_queue(queued_message)
    email_queue.queue[queue_id].status = EmailStatus.FAILED
    email_queue.queue[queue_id].retry_count = 3
    email_queue.queue[queue_id].error = "Error occurred"
    success = email_queue.retry_failed(queue_id)
    assert success is True
    retried_email = email_queue.queue[queue_id]
    assert retried_email.status.name == "QUEUED"
    assert retried_email.retry_count == 0
    assert retried_email.error is None

@pytest.mark.asyncio
async def test_get_email_status(email_queue, queued_message):
    queue_id = await email_queue.add_to_queue(queued_message)
    email_status = email_queue.get_email_status(queue_id)
    assert email_status is not None
    assert email_status.status.name == "QUEUED"
    assert email_queue.get_email_status("non-existent") is None

@pytest.mark.asyncio
async def test_max_retries(email_queue, queued_message):
    queue_id = await email_queue.add_to_queue(queued_message)
    queued_email = email_queue.queue[queue_id]
    for _ in range(email_queue.max_retries):
        queued_email.status = EmailStatus.SENDING
        queued_email.retry_count += 1
        queued_email.status = EmailStatus.QUEUED
    queued_email.status = EmailStatus.SENDING
    queued_email.retry_count += 1
    assert queued_email.retry_count > email_queue.max_retries
    assert queued_email.status.name == "FAILED"

@pytest.mark.asyncio
async def test_fastmail_queue_integration(queue_config, queued_message):
    fastmail = FastMail(queue_config)
    queue_id = await fastmail.send_message(queued_message, queue=True)
    assert queue_id is not None
    immediate_result = await fastmail.send_message(queued_message, queue=False)
    assert immediate_result is None

@pytest.mark.asyncio
async def test_scheduled_processing(email_queue, queued_message):
    schedule_time = datetime.now() + timedelta(seconds=2)
    queue_id = await email_queue.add_to_queue(queued_message, schedule_time=schedule_time)
    email_queue.start_processing()
    assert email_queue.queue[queue_id].status.name == "QUEUED"
    await asyncio.sleep(3)
    email_queue.stop_processing()
    assert email_queue.queue[queue_id].status.name == "SENT"