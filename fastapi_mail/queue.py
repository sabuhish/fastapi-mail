from typing import Optional, Dict
from enum import Enum
import asyncio
from datetime import datetime
from uuid import uuid4

from .schemas import MessageSchema
from .fastmail import FastMail

class EmailStatus(Enum):
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"

class QueuedEmail:
    def __init__(self, message: MessageSchema, template_name: Optional[str] = None):
        self.id = str(uuid4())
        self.message = message
        self.template_name = template_name
        self.status = EmailStatus.QUEUED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.retry_count = 0
        self.error = None
        self.scheduled_time = None

class EmailQueue:
    def __init__(self, fastmail: FastMail, max_retries: int = 3):
        self.fastmail = fastmail
        self.max_retries = max_retries
        self.queue: Dict[str, QueuedEmail] = {}
        self._processing = False
        self._task = None

    async def add_to_queue(self, message: MessageSchema, template_name: Optional[str] = None, schedule_time: Optional[datetime] = None) -> str:
        queued_email = QueuedEmail(message, template_name)
        if schedule_time:
            queued_email.scheduled_time = schedule_time
        self.queue[queued_email.id] = queued_email
        return queued_email.id

    async def process_queue(self):
        self._processing = True
        while self._processing:
            now = datetime.now()
            for email in list(self.queue.values()):
                if email.status == EmailStatus.QUEUED:
                    if email.scheduled_time and email.scheduled_time > now:
                        continue
                    try:
                        email.status = EmailStatus.SENDING
                        email.updated_at = datetime.now()
                        await self.fastmail._send_message(email.message, email.template_name)
                        email.status = EmailStatus.SENT
                        email.updated_at = datetime.now()
                    except Exception as e:
                        email.error = str(e)
                        email.retry_count += 1
                        if email.retry_count >= self.max_retries:
                            email.status = EmailStatus.FAILED
                        else:
                            email.status = EmailStatus.QUEUED
                        email.updated_at = datetime.now()
            await asyncio.sleep(1)

    def start_processing(self):
        if not self._task:
            self._task = asyncio.create_task(self.process_queue())

    def stop_processing(self):
        self._processing = False
        if self._task:
            self._task.cancel()
            self._task = None

    def get_queue_status(self) -> Dict[str, int]:
        status = {
            "total": len(self.queue),
            "queued": 0,
            "sending": 0,
            "sent": 0,
            "failed": 0
        }
        for email in self.queue.values():
            status[email.status.value] += 1
        return status

    def get_email_status(self, email_id: str) -> Optional[QueuedEmail]:
        return self.queue.get(email_id)

    def cancel_email(self, email_id: str) -> bool:
        if email_id in self.queue and self.queue[email_id].status == EmailStatus.QUEUED:
            del self.queue[email_id]
            return True
        return False

    def retry_failed(self, email_id: str) -> bool:
        if email_id in self.queue:
            email = self.queue[email_id]
            if email.status == EmailStatus.FAILED:
                email.status = EmailStatus.QUEUED
                email.retry_count = 0
                email.error = None
                email.updated_at = datetime.now()
                return True
        return False 