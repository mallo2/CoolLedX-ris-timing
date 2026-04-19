"""Commands for the CoolLEDX package."""

from __future__ import annotations

import abc
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import Future

from coolledx import (
    DEFAULT_BACKGROUND_COLOR,
    HeightTreatment,
    HorizontalAlignment,
    Mode,
    VerticalAlignment,
    WidthTreatment,
)

from coolledx.basic_protocol import BasicProtocol
from .hardware import CoolLED
from .render import (
    create_jt_payload,
)

DEFAULT_DEVICE_WIDTH = 96
DEFAULT_DEVICE_HEIGHT = 16

# Constants for byte escaping
ESCAPE_THRESHOLD = 0x04
ESCAPE_PREFIX = 0x02
ESCAPE_OFFSET = 0x04

# Constants for string truncation
MAX_TRUNCATED_LENGTH = 32

# Constants for value ranges
MAX_BYTE_VALUE = 0xFF
MIN_BYTE_VALUE = 0x00
MUSIC_BAR_COUNT = 8


class CoolLedError(Exception):
    """Base class for exceptions in this module."""


class ErrorCode(Enum):
    """Error codes returned by the device."""

    UNKNOWN = -1
    SUCCESS = 0x00
    TRANSMISSION_FAILED = 0x01
    DEVICE_ABNORMALITY = 0x02
    DATA_ERROR = 0x03
    DATA_LENGTH_ERROR = 0x04
    DATA_ID_ERROR = 0x05
    DATA_CHECKSUM_ERROR = 0x06

    @staticmethod
    def get_error_code_name(error_code: int | ErrorCode) -> str:
        """Return a human-readable error message for the given error code."""
        try:
            return ErrorCode(error_code).name
        except ValueError:
            return f"Unknown error code: {error_code:02X}"


class CommandStatus(Enum):
    """Status of the currently executing command."""

    NOT_STARTED = 0
    TRANSMITTED = 1
    ACKNOWLEDGED = 2
    ERROR = 3


class Command(abc.ABC, BasicProtocol):
    """Abstract base class for commands."""

    command_status: CommandStatus = CommandStatus.NOT_STARTED
    error_code: ErrorCode = ErrorCode.UNKNOWN
    future: Future | None = None
    hardware: CoolLED | None = None

    @abc.abstractmethod
    def get_command_raw_data_chunks(self) -> list[bytearray]:
        """Get the set of commands as a bytearray."""

    @staticmethod
    def escape_byte(byte: int) -> bytearray:
        """Bytes < 4 need to be escaped with 0x02."""
        if byte < ESCAPE_THRESHOLD:
            return bytearray([ESCAPE_PREFIX, byte + ESCAPE_OFFSET])
        return bytearray([byte])

    def set_hardware(self, hardware: CoolLED) -> None:
        """Set the hardware type."""
        self.hardware = hardware

    def get_hardware(self) -> CoolLED:
        """Get the hardware type."""
        if self.hardware is None:
            raise ValueError("Hardware not set")
        return self.hardware

    def set_future(self, future: Future) -> None:
        """Set the future for this command."""
        self.future = future

    def set_command_status(self, status: CommandStatus) -> None:
        """Set the status of the command."""
        self.command_status = status

    @property
    def get_device_width(self) -> int:
        """Get the device width, using default if not set."""
        try:
            return self.get_hardware().get_device_width()
        except ValueError:
            return DEFAULT_DEVICE_WIDTH

    @property
    def get_device_height(self) -> int:
        """Get the device height, using default if not set."""
        try:
            return self.get_hardware().get_device_height()
        except ValueError:
            return DEFAULT_DEVICE_HEIGHT

    @staticmethod
    def expect_notify() -> bool:
        """
        Check if we should expect a notification from the device.

        This only applies to commands that send data.
        """
        return True

    @staticmethod
    def is_raw_command() -> bool:
        """Check if this is a raw command that shouldn't be encoded/escaped."""
        return False

    @staticmethod
    def split_bytearray(data: bytearray, chunk_size: int) -> list[bytearray]:
        """Split a bytearray into chunks of the specified size."""
        chunks = [data]

        # split the last chunk as long as it is larger than chunk_size
        while True:
            i = len(chunks) - 1
            if len(chunks[i]) > chunk_size:
                chunks.append(chunks[i][chunk_size:])
                chunks[i] = chunks[i][:chunk_size]
            else:
                return chunks

    @staticmethod
    def get_xor_checksum(data: bytearray) -> int:
        """Calculate XOR checksum for the given data."""
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum

    def chop_up_data(self, data: bytearray, command: int) -> list[bytearray]:
        """Split data into chunks with headers and checksums."""
        # split the content into (128-byte) chunks
        raw_chunks = self.split_bytearray(data, 128)

        # add header information to the chunks
        chunks = []
        for chunk_id, raw_chunk in enumerate(raw_chunks):
            # create bytearray of for the content of the chunk including checksum
            formatted_chunk = bytearray()
            # unknown single 0x00 byte TODO
            formatted_chunk += b"\x00"
            # length of the payload before it was split (16-bit)
            formatted_chunk += len(data).to_bytes(2, byteorder="big")
            # current chunk-number (16-bit)
            formatted_chunk += chunk_id.to_bytes(2, byteorder="big")
            # size of the chunk (8-bit)
            formatted_chunk += len(raw_chunk).to_bytes(1, byteorder="big")
            # the data of the chunk
            formatted_chunk += raw_chunk
            # append XOR checksum to make the complete the formatted chunk
            formatted_chunk.append(self.get_xor_checksum(formatted_chunk))
            # Prepend our command byte for each chunk
            chunks.append(
                bytearray().join(
                    [command.to_bytes(1, byteorder="big"), formatted_chunk],
                ),
            )
        return chunks

    def get_command_chunks(self) -> list[bytearray]:
        """Get the command as a bytearray."""
        raw_data_chunks = self.get_command_raw_data_chunks()
        if self.is_raw_command():
            return raw_data_chunks
        return [self.create_command(x) for x in raw_data_chunks]

    def get_command_hexstr(self, *, append_newline: bool = True) -> str:
        """Get the command as a hex string."""
        hex_string = ""
        for chunk in self.get_command_chunks():
            hex_string += chunk.hex() + ("\n" if append_newline else "")
        return hex_string

    def truncated_command(self) -> str:
        """
        Return a string representation of the command that has been truncated to
        32 characters.
        """
        hexstr = self.get_command_hexstr(append_newline=False)
        if len(hexstr) > MAX_TRUNCATED_LENGTH:
            hexstr = hexstr[:MAX_TRUNCATED_LENGTH] + "..."
        return hexstr

    def __str__(self) -> str:
        """Return string representation of the command."""
        return f"{self.__class__.__name__}[{self.truncated_command()}]"

class SetMode(Command):
    """Set the text movement style for the scroller."""

    mode: Mode

    def __init__(self, mode: Mode) -> None:
        """Initialize with movement mode."""
        self.mode = mode

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        """Get the set mode command data."""
        return [
            bytearray.fromhex(f"{self.get_hardware().cmdbyte_mode():02x} {self.mode:02X}"),
        ]

    @staticmethod
    def expect_notify() -> bool:
        """Check if we should expect a notification from the device."""
        return False


class SetJT(Command):
    """Set the display image by loading from a JT file."""

    filename: str
    width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS
    height_treatment: HeightTreatment = HeightTreatment.CROP_PAD
    vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER
    horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE
    background_color: str

    def __init__(
        self,
        filename: str,
        background_color: str = DEFAULT_BACKGROUND_COLOR,
        width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
        height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
        vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
    ) -> None:
        """Initialize with JT filename and display options."""
        self.filename = filename
        self.background_color = background_color
        self.width_treatment = width_treatment
        self.height_treatment = height_treatment
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        """Get the set JT command data."""
        # raw_data = create_image_payload(
        raw_data, render_as_image = create_jt_payload(
            self.filename,
            self.get_device_width,
            self.get_device_height,
            self.background_color,
            self.width_treatment,
            self.height_treatment,
            self.horizontal_alignment,
            self.vertical_alignment,
        )
        hardware = self.get_hardware()
        return self.chop_up_data(
            raw_data,
            hardware.cmdbyte_image()
            if render_as_image
            else hardware.cmdbyte_animation(),
        )

    @staticmethod
    def expect_notify() -> bool:
        """Check if we should expect a notification from the device."""
        return True
