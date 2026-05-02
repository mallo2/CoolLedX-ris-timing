"""
CoolLED hardware definitions.

Describes the different CoolLED hardware we know. This is all pieced together
without any documentation.  If you have documentation, please share!

Generally, there are five classes of hardware, as far as I can tell:
- Basic:  This is the original CoolLED.  It has a fixed size, and a simple protocol.
- CoolLEDX:  This is the next generation of the CoolLED.  Simple protocol, varying matrix sizes.
"""

from .message_handler import MessageHandler, CoolLEDXMessageHandler


class CoolLED:
    """Base class for CoolLED hardware definitions."""

    device_width: int
    device_height: int
    device_color_mode: int
    device_firmware_version: int

    @classmethod
    def get_class_for_string(cls, device_type: str) -> type["CoolLED"]:
        """Get the class for the given device type."""
        if device_type == "CoolLEDX":
            return CoolLEDX
        else:
            raise ValueError(f"Unknown device type: {device_type}")

    def __init__(self, device_width: int, device_height: int, device_color_mode: int, device_firmware_version: int) -> None:
        """Initialize the hardware definition."""
        self.device_width = device_width
        self.device_height = device_height
        self.device_color_mode = device_color_mode
        self.device_firmware_version = device_firmware_version

    def get_device_width(self) -> int:
        """Get the device width."""
        return self.device_width

    def get_device_height(self) -> int:
        """Get the device height."""
        return self.device_height

    @staticmethod
    def cmdbyte_image() -> int:
        """Get the image command byte."""
        return 0x03

    @staticmethod
    def cmdbyte_animation() -> int:
        """Get the animation command byte."""
        return 0x04

    @staticmethod
    def cmdbyte_mode() -> int:
        """Get the mode command byte."""
        return 0x06

class CoolLEDX(CoolLED):
    """CoolLEDX hardware implementation."""

    def is_implemented(self) -> bool:
        """Check if the hardware is implemented."""
        return True

    def get_message_handler(self) -> MessageHandler:
        """Get the message handler for this hardware.  Uses the CoolLEDX message handler."""
        return CoolLEDXMessageHandler()
