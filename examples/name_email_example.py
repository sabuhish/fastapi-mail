"""
NameEmail example for FastAPI-Mail

Usage example for NameEmail format in recipients.
"""

from fastapi_mail import MessageSchema, MessageType


async def name_email_example():
    """NameEmail usage example"""

    # Configuration (replace with your actual email settings)
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

    # Create FastMail instance
    # fm = FastMail(conf)

    # Mixed recipient formats
    message = MessageSchema(
        subject="NameEmail Example - Mixed Formats",
        recipients=[
            "user@example.com",  # Simple email format
            "JohnDoe <john@example.com>",  # NameEmail format
            "SupportTeam <support@company.com>",  # NameEmail format
        ],
        cc=["Manager <manager@company.com>"],
        bcc=["Admin <admin@company.com>"],
        reply_to=["NoReply <noreply@company.com>"],
        body="""
        <h1>Hello!</h1>
        <p>This email demonstrates the NameEmail functionality.</p>
        <p>You can now specify recipients in the format "Name &lt;email@domain.com&gt;"</p>
        <p><strong>Note:</strong> Avoid spaces in names for best compatibility.</p>
        """,
        subtype=MessageType.html,
    )

    # Uncomment the line below to actually send the email
    # await fm.send_message(message)

    print("Message created successfully!")
    print(f"Recipients: {message.recipients}")
    print(f"CC: {message.cc}")
    print(f"BCC: {message.bcc}")
    print(f"Reply-To: {message.reply_to}")

    # Accessing name and email properties
    for recipient in message.recipients:
        print(f"Recipient: {recipient.name} <{recipient.email}>")
    
    print("\n" + "="*50)
    print("Common mistakes to avoid:")
    print("❌ 'John Doe support@company.com' (missing brackets)")
    print("❌ 'John Doe <support@company.com' (missing closing bracket)")
    print("❌ 'John Doe <support @company.com>' (space in email)")
    print("✅ 'JohnDoe <support@company.com>' (correct)")
    print("✅ 'user@example.com' (simple format)")


if __name__ == "__main__":
    import asyncio

    asyncio.run(name_email_example())
