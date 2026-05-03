from __future__ import annotations

import abc
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import Future

from core.basic_protocol import BasicProtocol
from core.hardware import CoolLEDX
from core.render import create_jt_payload

class ErrorCode(Enum):
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
        try:
            return ErrorCode(error_code).name
        except ValueError:
            return f"Unknown error code: {error_code:02X}"


class CommandStatus(Enum):
    NOT_STARTED = 0
    TRANSMITTED = 1
    ACKNOWLEDGED = 2
    ERROR = 3


class Command(abc.ABC, BasicProtocol):
    command_status: CommandStatus = CommandStatus.NOT_STARTED
    error_code: ErrorCode = ErrorCode.UNKNOWN
    future: Future | None = None
    hardware: CoolLEDX | None = None

    @abc.abstractmethod
    def get_command_raw_data_chunks(self) -> list[bytearray]:
        """Get the set of commands as a bytearray."""

    @staticmethod
    def escape_byte(byte: int) -> bytearray:
        if byte < 0x04:
            return bytearray([0x02, byte + 0x04])
        return bytearray([byte])

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
        if len(hexstr) > 32:
            hexstr = hexstr[:32] + "..."
        return hexstr

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.truncated_command()}]"

class SetMode(Command):
    def __init__(self) -> None:
        # Initialization in the STATIC mode
        self.mode = 0x01

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        return [bytearray.fromhex(f"{CoolLEDX.cmdbyte_mode():02x} {self.mode:02X}"),]

    @staticmethod
    def expect_notify() -> bool:
        return False


class SetJT(Command):
    filename: str

    def __init__(self, filename: str = "generated.jt") -> None:
        self.filename = filename

    def get_command_raw_data_chunks(self) -> list[bytearray]:
        raw_data = create_jt_payload(self.filename)
        return self.chop_up_data(
            raw_data,
            CoolLEDX.cmdbyte_image()
        )

    @staticmethod
    def expect_notify() -> bool:
        return True
