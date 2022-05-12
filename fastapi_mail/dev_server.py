import logging
from aiosmtpd.controller import Controller


logging.basicConfig(level=logging.DEBUG)


class DevMailHandler:
    async def handle_DATA(self, server, session, envelope):
        logging.debug("\n\rNEW MAIL".strip())
        for ln in envelope.content.decode("utf8", errors="replace").splitlines():
            logging.debug(f"{ln}".strip())
        return "250 Message accepted for delivery"


dev_controller = Controller(DevMailHandler(), hostname="127.0.0.1")
