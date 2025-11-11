"""
Bulk email example demonstrating FastAPI-Mail's ability to send multiple messages in one call.

Run this file to see how you can prepare multiple MessageSchema instances and
send them over a single SMTP connection to avoid rate limiting or connection
overhead.
"""

from typing import List

from fastapi_mail import MessageSchema, MessageType, NameEmail


async def main() -> None:
    # Replace these settings with your actual SMTP credentials.
    # from fastapi_mail import ConnectionConfig
    # conf = ConnectionConfig(
    #     MAIL_USERNAME="your_username",
    #     MAIL_PASSWORD="your_password",
    #     MAIL_FROM="your_email@example.com",
    #     MAIL_PORT=587,
    #     MAIL_SERVER="smtp.gmail.com",
    #     MAIL_STARTTLS=True,
    #     MAIL_SSL_TLS=False,
    #     USE_CREDENTIALS=True,
    #     VALIDATE_CERTS=True,
    # )
    # fm = FastMail(conf)

    # Example messages that would be sent in a single SMTP session.
    messages: List[MessageSchema] = [
        MessageSchema(
            subject="Welcome!",
            recipients=[NameEmail(email="user1@example.com", name="John Doe")],
            body="<p>Thanks for joining us.</p>",
            subtype=MessageType.html,
        ),
        MessageSchema(
            subject="Verify your email",
            recipients=[NameEmail(email="user2@example.com", name="Jane Doe")],
            body="<p>Please click the verification link.</p>",
            subtype=MessageType.html,
        ),
        MessageSchema(
            subject="Monthly update",
            recipients=[NameEmail(email="user3@example.com", name="Jim Beam")],
            body="<p>Here are the latest updates.</p>",
            subtype=MessageType.html,
        ),
    ]

    # Uncomment the following line once you configure FastMail above.
    # await fm.send_message(messages)

    print("Prepared", len(messages), "messages for bulk sending.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
