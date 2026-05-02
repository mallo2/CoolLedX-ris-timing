from __future__ import annotations

import asyncio
import logging
import sys
from time import sleep
from typing import NoReturn

from bleak.exc import BleakError
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from pro.apiCall import get_lap_time
from pro.generate_jt import generate_jt
from pro.lap_time_converter import format_time

from core.client import Client
from core.commands import (
    SetJT,
    SetMode,
)

LOGGER = logging.getLogger(__name__)

async def _process_device(device: BLEDevice, coolledx_devices: list[BLEDevice])-> None:
    if device.name == "CoolLEDX":
        coolledx_devices.append(device)
        print()
        print("-" * 80)
        print(f"Device: {device.name} ({device.address})")

async def _process_all_devices(devices) -> list[BLEDevice]:
    coolledx_devices = []
    for d, _ in devices.values():
        try:
            await _process_device(d, coolledx_devices)
        except (BleakError, EOFError, OSError, IndexError, StopIteration) as e:
            print(f"Error processing device {d.address}: {e}")
    return coolledx_devices

def _format_device_option(index: int, device: BLEDevice, advertisement: AdvertisementData) -> str:
    """Format a scan result for interactive selection."""
    name = device.name or "<sans nom>"
    rssi = getattr(advertisement, "rssi", "?")
    return f"[{index}] {name} — {device.address} (RSSI: {rssi})"


def prompt_device_selection(devices: list[BLEDevice]) -> BLEDevice:
    while True:
        raw_choice = input(f"Choisir un appareil [1-{len(devices)}]: ").strip()
        try:
            selected_index = int(raw_choice)
        except ValueError:
            print("Veuillez saisir un numéro valide.")
            continue
        if 1 <= selected_index <= len(devices):
            return devices[selected_index - 1]
        print(f"Veuillez choisir un numéro entre 1 et {len(devices)}.")


def prompt_text_size():
    while True:
        raw_value = input("Taille du texte (large | small) : ").strip()
        try:
            text_size = raw_value.lower()
            if text_size in ['large', 'small']:
                return text_size
        except ValueError:
            print("Veuillez saisir 'large' ou 'small'.")
            continue

def prompt_car_number():
    while True:
        raw_value = input("Numéro de voiture : ").strip()
        try:
            car_number = int(raw_value)
        except ValueError:
            print("Veuillez saisir un numéro entier valide.")
            continue
        if car_number > 0:
            return car_number
        print("Le numéro de voiture doit être supérieur à zéro.")


def handle_connection_error(
    error: TimeoutError | BleakError | asyncio.CancelledError,
    device_address: str | None,
) -> NoReturn:
    """Handle connection errors with helpful error messages and exit."""
    if isinstance(error, TimeoutError):
        LOGGER.error("Connection timed out while trying to connect to the LED sign")
        if device_address:
            print(
                f"Error: Connection timed out while connecting to device {device_address}",
            )
            print("Suggestions:")
            print("  - Ensure the LED sign is powered on and in range")
            print("  - Check that the MAC address is correct")
            print("  - Try moving closer to the device")
            print("  - Ensure no other devices are connected to the sign")
        else:
            print("Error: Connection timed out while scanning for LED signs")
            print("Suggestions:")
            print("  - Ensure the LED sign is powered on and in range")
            print("  - Try specifying the device MAC address with -a option")
            print("  - Check that the device name is correct (use -d option)")
    elif isinstance(error, BleakError):
        LOGGER.error("Bluetooth error occurred: %s", error)
        print(f"Error: Bluetooth communication failed - {error}")
        print("Suggestions:")
        print("  - Check that Bluetooth is enabled on your system")
        print("  - Ensure the LED sign is not connected to another device")
        print("  - Try restarting the LED sign")
        print("  - Check system Bluetooth permissions")
    elif isinstance(error, asyncio.CancelledError):
        LOGGER.error("Connection was cancelled")
        print("Error: Connection was cancelled or interrupted")
        print("Suggestions:")
        print("  - Try running the command again")
        print("  - Ensure stable Bluetooth connection")
    else:
        LOGGER.error("Unexpected error occurred: %s", error)
        print(f"Error: Unexpected error occurred - {error}")
        print("Run with --log DEBUG for more detailed information")

    sys.exit(1)


async def send_content_commands(client: Client, text: str, size: str) -> None:
    """Send content commands (text, image, animation, JT) to the LED sign."""
    LOGGER.info("Sending text command: %s", text)
    generate_jt(text, "white", size)
    await client.send_command(SetMode())
    await client.send_command(SetJT())

async def main() -> None:
    logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",)

    try:
        LOGGER.info("Starting Bluetooth scan before device selection")
        devices = await BleakScanner.discover(timeout=10, return_adv=True)
        if not devices:
            print("Aucun appareil compatible trouvé.")
            sys.exit(1)
        coolledx_devices = await _process_all_devices(devices)
        selected_device = prompt_device_selection(coolledx_devices)
        selected_address = selected_device.address
        LOGGER.info("Selected device %s (%s)", selected_device.name, selected_address)
        text_size = prompt_text_size()
        car_number = prompt_car_number()

        # Create client with configurable timeout and retry settings
        client_config = {
            "address": selected_address,
            "device_name": selected_device.name,
            "connection_timeout": 10,
            "connection_retries": 5,
        }
        LOGGER.info(
            "Connecting to LED sign with timeout=%.1fs, retries=%d",
            10,
            5,
        )

        async with Client(**client_config) as client:
            LOGGER.info("Successfully connected to LED sign")
            last_lap_time = None
            while True:
                LOGGER.info("Retrieving lap time for car number %s", car_number)
                print(f"Récupération des données pour la voiture #{car_number}...")
                lap_time = get_lap_time(car_number)
                if last_lap_time is None or last_lap_time != lap_time:
                    last_lap_time = lap_time
                    formatted_time = format_time(lap_time)
                    text = formatted_time if text_size == 'large' else f"#{car_number} {formatted_time}"
                    await send_content_commands(client, text, text_size)
                    LOGGER.info("All commands sent successfully")
                    print("Mise à jour du panneau terminée avec succès")
                    sleep(1)

    except (TimeoutError, BleakError, asyncio.CancelledError) as e:
        handle_connection_error(e, selected_address)
    except Exception as e:
        LOGGER.exception("Unexpected error occurred")
        print(f"Error: Failed to update LED sign - {e}")
        print("Run with --log DEBUG for more detailed information")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except (OSError, RuntimeError) as e:
        print(f"Fatal error: {e}")
        sys.exit(1)