from fastapi_mail.config import ConnectionConfig
from fastapi_mail.fastmail import FastMail
from fastapi_mail.schemas import MessageSchema, MultipartSubtypeEnum

from . import email_utils

__version__ = "0.4.1"


__author__ = "sabuhi.shukurov@gmail.com"


__all__ = [
    "FastMail",
    "ConnectionConfig",
    "MessageSchema",
    "email_utils",
    "MultipartSubtypeEnum",
]


from fastapi_mail.dev_server import dev_controller


def server_main():
    try:
        dev_controller.start()
    except KeyboardInterrupt:
        dev_controller.stop()


if __name__ == "__main__":
    server_main()
