from aiosmtpd.controller import Controller


class DevMailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
           print(f'{ln}'.strip())
        return '250 Message accepted for delivery'


dev_controller = Controller(DevMailHandler())

# this should be in the main file?
# controller.start()
# to stop the server once done
# controller.stop()