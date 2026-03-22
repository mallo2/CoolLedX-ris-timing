"""
Basic protocol implementation for CoolLED devices.

This is the protocol that is used by the CoolLEDX and related devices.  It is
responsible for encoding and decoding the commands that are sent to the device.
"""

from __future__ import annotations
import re


class BasicProtocol:
    """Basic protocol implementation for CoolLED devices."""

    def create_command(self, raw_data: bytearray) -> bytearray:
        """Create the command.  In the basic protocol, the command protocol is
        0x01 [data] 0x03 to handle the framing."""
        extended_data = bytearray().join(
            [len(raw_data).to_bytes(2, byteorder="big"), raw_data],
        )
        return bytearray().join([b"\x01", self.escape_bytes(extended_data), b"\x03"])

    @staticmethod
    def escape_bytes(bytes_to_escape: bytearray) -> bytes:
        """Escape special bytes in the data for transmission."""
        data = re.sub(
            re.compile(b"\x02", re.MULTILINE),
            b"\x02\x06",
            bytes_to_escape,
        )  # needs to be first
        data = re.sub(re.compile(b"\x01", re.MULTILINE), b"\x02\x05", data)
        return re.sub(re.compile(b"\x03", re.MULTILINE), b"\x02\x07", data)
