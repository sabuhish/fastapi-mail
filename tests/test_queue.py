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
        body="Test body",
        subtype=MessageType.plain
    )

@pytest.fixture
def queue_config(mail_config):
    """Reuse the existing mail_config fixture but ensure SUPPRESS_SEND is True"""
    mail_config["SUPPRESS_SEND"] = 1
    return ConnectionConfig(**mail_config)

@pytest.fixture
def email_queue(queue_config):
    fastmail = FastMail(queue_config)
    return EmailQueue(fastmail)

@pytest.mark.asyncio
async def test_add_to_queue(email_queue, queued_message):
    # Test adding email to queue
    queue_id = await email_queue.add_to_queue(queued_message)
    
    assert queue_id in email_queue.queue
    assert email_queue.queue[queue_id].status == EmailStatus.QUEUED
    assert email_queue.queue[queue_id].message == queued_message
    assert email_queue.queue[queue_id].retry_count == 0

@pytest.mark.asyncio
async def test_scheduled_email(email_queue, queued_message):
    # Schedule email for future delivery
    schedule_time = datetime.now() + timedelta(hours=1)
    queue_id = await email_queue.add_to_queue(queued_message, schedule_time=schedule_time)
    
    queued_email = email_queue.queue[queue_id]
    assert queued_email.scheduled_time == schedule_time
    assert queued_email.status == EmailStatus.QUEUED

@pytest.mark.asyncio
async def test_process_queue(email_queue, queued_message):
    # Add message to queue
    queue_id = await email_queue.add_to_queue(queued_message)
    
    # Start processing
    email_queue.start_processing()
    
    # Wait briefly for processing
    await asyncio.sleep(2)
    
    # Stop processing
    email_queue.stop_processing()
    
    # Check if message was processed
    processed_email = email_queue.queue[queue_id]
    assert processed_email.status == EmailStatus.SENT

@pytest.mark.asyncio
async def test_queue_status(email_queue, queued_message):
    # Add multiple messages with different statuses
    queue_id1 = await email_queue.add_to_queue(queued_message)
    queue_id2 = await email_queue.add_to_queue(queued_message)
    
    # Manually modify status of second email
    email_queue.queue[queue_id2].status = EmailStatus.FAILED
    email_queue.queue[queue_id2].retry_count = 3
    
    status = email_queue.get_queue_status()
    assert status["total"] == 2
    assert status["queued"] == 1
    assert status["failed"] == 1

@pytest.mark.asyncio
async def test_cancel_email(email_queue, queued_message):
    # Add message to queue
    queue_id = await email_queue.add_to_queue(queued_message)
    
    # Cancel the email
    success = email_queue.cancel_email(queue_id)
    assert success is True
    assert queue_id not in email_queue.queue

    # Try to cancel non-existent email
    success = email_queue.cancel_email("non-existent-id")
    assert success is False

@pytest.mark.asyncio
async def test_retry_failed_email(email_queue, queued_message):
    # Add message and mark as failed
    queue_id = await email_queue.add_to_queue(queued_message)
    email_queue.queue[queue_id].status = EmailStatus.FAILED
    email_queue.queue[queue_id].retry_count = 3
    email_queue.queue[queue_id].error = "Test error"
    
    # Retry the failed email
    success = email_queue.retry_failed(queue_id)
    assert success is True
    
    # Check if email was reset properly
    retried_email = email_queue.queue[queue_id]
    assert retried_email.status == EmailStatus.QUEUED
    assert retried_email.retry_count == 0
    assert retried_email.error is None

@pytest.mark.asyncio
async def test_get_email_status(email_queue, queued_message):
    # Add message to queue
    queue_id = await email_queue.add_to_queue(queued_message)
    
    # Get status of queued email
    email_status = email_queue.get_email_status(queue_id)
    assert email_status is not None
    assert email_status.status == EmailStatus.QUEUED
    
    # Get status of non-existent email
    email_status = email_queue.get_email_status("non-existent-id")
    assert email_status is None

@pytest.mark.asyncio
async def test_max_retries(email_queue, queued_message):
    # Add message to queue
    queue_id = await email_queue.add_to_queue(queued_message)
    queued_email = email_queue.queue[queue_id]
    
    # Simulate multiple failures
    for _ in range(email_queue.max_retries):
        queued_email.status = EmailStatus.SENDING
        queued_email.retry_count += 1
        queued_email.status = EmailStatus.QUEUED
    
    # Process one more time
    queued_email.status = EmailStatus.SENDING
    queued_email.retry_count += 1
    
    # Check if email is marked as failed after max retries
    assert queued_email.retry_count > email_queue.max_retries
    assert queued_email.status == EmailStatus.FAILED

@pytest.mark.asyncio
async def test_fastmail_queue_integration(queue_config, queued_message):
    # Test integration with FastMail class
    fastmail = FastMail(queue_config)
    
    # Queue a message
    queue_id = await fastmail.send_message(queued_message, queue=True)
    assert queue_id is not None
    
    # Send message immediately
    immediate_result = await fastmail.send_message(queued_message, queue=False)
    assert immediate_result is None

@pytest.mark.asyncio
async def test_scheduled_processing(email_queue, queued_message):
    # Schedule email for near future
    schedule_time = datetime.now() + timedelta(seconds=2)
    queue_id = await email_queue.add_to_queue(queued_message, schedule_time=schedule_time)
    
    # Start processing
    email_queue.start_processing()
    
    # Check immediate status
    assert email_queue.queue[queue_id].status == EmailStatus.QUEUED
    
    # Wait for scheduled time to pass
    await asyncio.sleep(3)
    
    # Stop processing
    email_queue.stop_processing()
    
    # Check if message was processed after scheduled time
    assert email_queue.queue[queue_id].status == EmailStatus.SENT 