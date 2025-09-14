"""
"""


class CoolLED:


        return 0x03

        return 0x04

        return 0x06









class CoolLEDX(CoolLED):

    def is_implemented(self) -> bool:
        """Check if the hardware is implemented."""
        return True

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDX message handler."""
        return CoolLEDXMessageHandler()
