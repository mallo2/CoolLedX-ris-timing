class CoolLEDX:
    device_color_mode: int
    device_firmware_version: int

    def __init__(self, device_color_mode: int, device_firmware_version: int) -> None:
        self.device_color_mode = device_color_mode
        self.device_firmware_version = device_firmware_version

    @staticmethod
    def cmdbyte_image() -> int:
        return 0x03

    @staticmethod
    def cmdbyte_mode() -> int:
        return 0x06
