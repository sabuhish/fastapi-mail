from typing import List

from pydantic import BaseModel, NameEmail


class EmailSchema(BaseModel):
    email: List[
        NameEmail
    ]  # Supports both "user@example.com" and "Name <user@example.com>" formats
    # Note: Avoid spaces in names for best compatibility (e.g., "JohnDoe <john@example.com>")
