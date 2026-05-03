from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Self, Any, Coroutine

from bleak import (
    BleakClient,
    BleakScanner, BLEDevice,
)
from bleak.exc import BleakError

if TYPE_CHECKING:
    from bleak.backends.characteristic import BleakGATTCharacteristic
    from bleak.backends.device import BLEDevice

from core.commands import Command, CommandStatus, ErrorCode

SERVICE_FFF0_CHAR = "0000fff1-0000-1000-8000-00805f9b34fb"

LOGGER = logging.getLogger(__name__)


class Client:
    device_address: str | None = None
    bleak_client: BleakClient | None = None
    ble_device: BLEDevice | None = None
    characteristic_uuid: str
    connection_timeout: float
    command_timeout: float
    connection_retries: int
    current_command: Command | None = None

    def __init__(
        self,
        address: str | None,
        device_name: str | None,
        connection_timeout: float = 10,
        command_timeout: float = 1,
        connection_retries: int = 5,
    ) -> None:
        self.device_address = address
        self.device_name = device_name
        self.connection_timeout = connection_timeout
        self.command_timeout = command_timeout
        self.connection_retries = connection_retries
        self.characteristic_uuid = SERVICE_FFF0_CHAR

    # Support async context management

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        """Exit async context manager."""
        await self.disconnect()

    async def connect(self) -> None:
        LOGGER.debug("Initiating a connection to the device: %s", self.device_address)
        retries_remaining = self.connection_retries
        while retries_remaining > 0:
            try:
                retries_remaining -= 1
                ble_device = await self._discover_device()

                if ble_device is None:
                    LOGGER.debug("Unable to locate a CoolLED* device when scanning.")
                    raise BleakError(
                        "Unable to locate a CoolLED* device when scanning.",
                    )

                bleak_client = BleakClient(
                    ble_device,
                    timeout=self.connection_timeout,
                    disconnected_callback=self.handle_disconnect,
                )
                LOGGER.debug("Connecting to device: %s", ble_device)
                await bleak_client.connect()
                LOGGER.debug("Connected to device: %s", ble_device)
                self.ble_device = ble_device
                self.bleak_client = bleak_client
                break
            except (BleakError, TimeoutError, asyncio.CancelledError) as e:
                LOGGER.warning(
                    "Connection to CoolLED* (address: %s) received exception: %s",
                    self.device_address,
                    e,
                )
                if retries_remaining <= 0:
                    LOGGER.exception(
                        "Connection failed after %s attempts.",
                        self.connection_retries,
                    )
                    raise
                LOGGER.info(
                    "Retrying connection...",
                )
                await asyncio.sleep(1)
        await self.bleak_client.start_notify(
            self.characteristic_uuid,
            self.handle_notify,
        )

    async def _discover_device(self) -> BLEDevice | None:
        LOGGER.debug("Scanning for devices...")

        devices = await BleakScanner.discover(
            timeout=self.connection_timeout,
            return_adv=True,
        )

        target_device_name = (
            self.device_name if self.device_name else "CoolLEDX"
        )

        for device, advertisement_data in devices.values():
            if self.device_address is not None:
                if device.address.lower() != self.device_address.lower():
                    continue

            LOGGER.debug("Found target device: %s (%s)", device.name, device.address)

            if not advertisement_data.manufacturer_data:
                LOGGER.warning("Device %s has no manufacturer data", device.address)
                continue

            try:
                value = next(iter(advertisement_data.manufacturer_data.values()))

                if len(value) < 11:
                    LOGGER.warning(
                        "Device %s manufacturer data too short: %s",
                        device.address,
                        value.hex(),
                    )
                    continue

                height = value[6]
                width = value[7] << 8 | value[8]

                if width != 96 or height != 16:
                    raise ValueError("Device is not compatible")

            except (IndexError, StopIteration) as e:
                LOGGER.warning(
                    "Failed to parse manufacturer data for device %s: %s",
                    device.address,
                    e,
                )
                continue
            else:
                return device

        LOGGER.debug("Target device not found in scan results")
        return None

    def handle_notify(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        if sender.uuid == self.characteristic_uuid:
            LOGGER.debug("Received notification: from %s data: %s", sender, data.hex())
            if self.current_command:
                self.current_command.set_command_status(CommandStatus.ACKNOWLEDGED)
                self.current_command.error_code = ErrorCode.SUCCESS
                if self.current_command.future:
                    self.current_command.future.set_result(0)
            else:
                LOGGER.error("Received a notification without a current command.")

    @staticmethod
    def handle_disconnect(client: BleakClient) -> None:
        LOGGER.info("Disconnected from device: %s", client)

    async def force_connected(self) -> None:
        if self.bleak_client is None or not self.bleak_client.is_connected:
            await self.connect()

    async def send_command(self, command: Command) -> None:
        await self.force_connected()
        chunks = command.get_command_chunks()
        try:
            for chunk in chunks:
                LOGGER.debug("Sending chunk: %s", chunk.hex())
                self.current_command = command
                command.command_status = CommandStatus.TRANSMITTED
                command.set_future(asyncio.get_event_loop().create_future())
                await self.write_raw(chunk, expect_response=command.expect_notify())
                if command.expect_notify() and command.future:
                    await asyncio.wait_for(command.future, timeout=self.command_timeout)

        except Exception:
            LOGGER.exception("Error sending command: %s", command)
            self.current_command = None
            raise

    async def write_raw(self, data: bytearray, *, expect_response: bool = False) -> None:
        if self.bleak_client is None:
            raise TypeError("bleak_client should not be None after connection.")
        await self.bleak_client.write_gatt_char(
            self.characteristic_uuid,
            data,
            response=expect_response,
        )

    async def disconnect(self) -> None:
        if self.bleak_client is not None:
            LOGGER.debug("Disconnecting from device: %s", self.bleak_client)
            await self.bleak_client.stop_notify(self.characteristic_uuid)
