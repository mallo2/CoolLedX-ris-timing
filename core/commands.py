"""Commands for the CoolLEDX package."""

from __future__ import annotations

import abc
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import Future

from core.basic_protocol import BasicProtocol
from hardware import CoolLEDX
from render import (
    create_jt_payload,
)

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
    hardware: CoolLEDX | None = None

    @abc.abstractmethod
    def get_command_raw_data_chunks(self) -> list[bytearray]:
        """Get the set of commands as a bytearray."""

    @staticmethod
    def escape_byte(byte: int) -> bytearray:
        if byte < ESCAPE_THRESHOLD:
            return bytearray([ESCAPE_PREFIX, byte + ESCAPE_OFFSET])
        return bytearray([byte])

    def set_hardware(self, hardware: CoolLEDX) -> None:
        self.hardware = hardware

    def get_hardware(self) -> CoolLEDX:
        if self.hardware is None:
            raise ValueError("Hardware not set")
        return self.hardware

    def set_future(self, future: Future) -> None:
        self.future = future

    def set_command_status(self, status: CommandStatus) -> None:
        self.command_status = status

    @staticmethod
    def expect_notify() -> bool:
        return True

    @staticmethod
    def is_raw_command() -> bool:
        return False

    @staticmethod
    def split_bytearray(data: bytearray, chunk_size: int) -> list[bytearray]:
        chunks = [data]

        while True:
            i = len(chunks) - 1
            if len(chunks[i]) > chunk_size:
                chunks.append(chunks[i][chunk_size:])
                chunks[i] = chunks[i][:chunk_size]
            else:
                return chunks

    @staticmethod
    def get_xor_checksum(data: bytearray) -> int:
        checksum = 0
        for b in data:
            checksum ^= b
        return checksum

    def chop_up_data(self, data: bytearray, command: int) -> list[bytearray]:
        raw_chunks = self.split_bytearray(data, 128)

        chunks = []
        for chunk_id, raw_chunk in enumerate(raw_chunks):
            formatted_chunk = bytearray()
            formatted_chunk += b"\x00"
            formatted_chunk += len(data).to_bytes(2, byteorder="big")
            formatted_chunk += chunk_id.to_bytes(2, byteorder="big")
            formatted_chunk += len(raw_chunk).to_bytes(1, byteorder="big")
            formatted_chunk += raw_chunk
            formatted_chunk.append(self.get_xor_checksum(formatted_chunk))
            chunks.append(
                bytearray().join(
                    [command.to_bytes(1, byteorder="big"), formatted_chunk],
                ),
            )
        return chunks

    def get_command_chunks(self) -> list[bytearray]:
        raw_data_chunks = self.get_command_raw_data_chunks()
        if self.is_raw_command():
            return raw_data_chunks
        return [self.create_command(x) for x in raw_data_chunks]

    def get_command_hexstr(self, *, append_newline: bool = True) -> str:
        hex_string = ""
        for chunk in self.get_command_chunks():
            hex_string += chunk.hex() + ("\n" if append_newline else "")
        return hex_string

    def truncated_command(self) -> str:
        hexstr = self.get_command_hexstr(append_newline=False)
        if len(hexstr) > MAX_TRUNCATED_LENGTH:
            hexstr = hexstr[:MAX_TRUNCATED_LENGTH] + "..."
        return hexstr

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.truncated_command()}]"

class SetMode(Command):
    def __init__(self) -> None:
        # Initialization in the STATIC mode
        self.mode = 0x01

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [bytearray.fromhex(f"{self.get_hardware().cmdbyte_mode():02x} {self.mode:02X}"),]

    @staticmethod
    def expect_notify() -> bool:
        return False


class SetJT(Command):
    filename: str

    def __init__(self, filename: str = "generated.jt") -> None:
        self.filename = filename

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        raw_data, render_as_image = create_jt_payload(
            self.filename,
        )
        hardware = self.get_hardware()
        return self.chop_up_data(
            raw_data,
            hardware.cmdbyte_image()
        )

    @staticmethod
    def expect_notify() -> bool:
        return True
