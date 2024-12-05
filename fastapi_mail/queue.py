from typing import List, Optional, Dict
from enum import Enum
import asyncio
import time
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

    async def add_to_queue(self, message: MessageSchema, template_name: Optional[str] = None, 
                          schedule_time: Optional[datetime] = None) -> str:
        """Add email to queue and return queue ID"""
        queued_email = QueuedEmail(message, template_name)
        if schedule_time:
            queued_email.scheduled_time = schedule_time
        self.queue[queued_email.id] = queued_email
        return queued_email.id

    async def process_queue(self):
        """Process all queued emails"""
        self._processing = True
        while self._processing:
            current_time = datetime.now()
            for email_id, queued_email in list(self.queue.items()):
                if queued_email.status == EmailStatus.QUEUED:
                    if queued_email.scheduled_time and queued_email.scheduled_time > current_time:
                        continue
                    
                    try:
                        queued_email.status = EmailStatus.SENDING
                        await self.fastmail.send_message(
                            queued_email.message,
                            template_name=queued_email.template_name
                        )
                        queued_email.status = EmailStatus.SENT
                        queued_email.updated_at = datetime.now()
                    except Exception as e:
                        queued_email.error = str(e)
                        queued_email.retry_count += 1
                        if queued_email.retry_count >= self.max_retries:
                            queued_email.status = EmailStatus.FAILED
                        else:
                            queued_email.status = EmailStatus.QUEUED
                        queued_email.updated_at = datetime.now()
            
            await asyncio.sleep(1)

    def start_processing(self):
        """Start processing queue in background"""
        if not self._task:
            self._task = asyncio.create_task(self.process_queue())

    def stop_processing(self):
        """Stop processing queue"""
        self._processing = False
        if self._task:
            self._task.cancel()
            self._task = None

    def get_queue_status(self) -> Dict:
        """Get current queue status"""
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
        """Get status of specific email"""
        return self.queue.get(email_id)

    def cancel_email(self, email_id: str) -> bool:
        """Cancel a queued email"""
        if email_id in self.queue:
            email = self.queue[email_id]
            if email.status == EmailStatus.QUEUED:
                del self.queue[email_id]
                return True
        return False

    def retry_failed(self, email_id: str) -> bool:
        """Retry a failed email"""
        if email_id in self.queue:
            email = self.queue[email_id]
            if email.status == EmailStatus.FAILED:
                email.status = EmailStatus.QUEUED
                email.retry_count = 0
                email.error = None
                email.updated_at = datetime.now()
                return True
        return False 