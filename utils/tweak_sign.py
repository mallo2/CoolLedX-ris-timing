from __future__ import annotations

import asyncio
import logging
import sys
from typing import TYPE_CHECKING, NoReturn

from bleak.exc import BleakError

from utils.apiCall import get_lap_time
from utils.generate_jt import generate_jt
from utils.lap_time_converter import format_time

if TYPE_CHECKING:
    import argparse

from coolledx.argparser import parse_standard_arguments
from coolledx.client import Client
from coolledx.commands import (
    SetJT,
    SetMode,
)

LOGGER = logging.getLogger(__name__)


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


async def send_content_commands(client: Client, args: argparse.Namespace, text) -> None:
    """Send content commands (text, image, animation, JT) to the LED sign."""
    LOGGER.info("Sending text command: %s", text)
    generate_jt(text, args.color, args.size)
    await client.send_command(
        SetJT(
            "generated.jt",
             background_color="black",
             width_treatment=args.width_treatment,
             height_treatment=args.height_treatment,
            horizontal_alignment=args.horizontal_alignment,
            vertical_alignment=args.vertical_alignment,
        ),
    )


async def send_setting_commands(client: Client, args: argparse.Namespace) -> None:
    """Send setting commands (mode) to the LED sign."""
    if args.mode >= 0:
        LOGGER.info("Setting mode: %s", args.mode)
        await client.send_command(SetMode(args.mode))


async def main() -> None:
    """Send commands to the CoolLEDX sign."""
    args = parse_standard_arguments()

    # Configure logging with more detailed format for better debugging
    logging.basicConfig(
        level=args.log.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Create client with configurable timeout and retry settings
        client_config = {
            "address": args.address,
            "device_name": args.device_name,
            "connection_timeout": args.connection_timeout,
            "connection_retries": args.connection_retries,
        }
        LOGGER.info(
            "Connecting to LED sign with timeout=%.1fs, retries=%d",
            args.connection_timeout,
            args.connection_retries,
        )

        async with Client(**client_config) as client:
            LOGGER.info("Successfully connected to LED sign")
            lap_time = get_lap_time(args.number)
            text = format_time(lap_time) if args.size == 'large' else f"#{args.number} {format_time(lap_time)}"

            await send_content_commands(client, args, text)
            await send_setting_commands(client, args)

            LOGGER.info("All commands sent successfully")
            print("LED sign update completed successfully")

    except (TimeoutError, BleakError, asyncio.CancelledError) as e:
        handle_connection_error(e, args.address)
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
