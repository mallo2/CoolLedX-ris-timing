import re

class BasicProtocol:

    def create_command(self, raw_data: bytearray) -> bytearray:
        extended_data = bytearray().join(
            [len(raw_data).to_bytes(2, byteorder="big"), raw_data],
        )
        return bytearray().join([b"\x01", self.escape_bytes(extended_data), b"\x03"])

    @staticmethod
    def escape_bytes(bytes_to_escape: bytearray) -> bytes:
        data = re.sub(
            re.compile(b"\x02", re.MULTILINE),
            b"\x02\x06",
            bytes_to_escape,
        )  # needs to be first
        data = re.sub(re.compile(b"\x01", re.MULTILINE), b"\x02\x05", data)
        return re.sub(re.compile(b"\x03", re.MULTILINE), b"\x02\x07", data)
