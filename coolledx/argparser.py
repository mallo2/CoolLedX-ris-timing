import argparse

from coolledx import (
    DEFAULT_COLOR,
    DEFAULT_HEIGHT_TREATMENT,
    DEFAULT_HORIZONTAL_ALIGNMENT,
    DEFAULT_LOGGING,
    DEFAULT_MODE,
    DEFAULT_VERTICAL_ALIGNMENT,
    DEFAULT_WIDTH_TREATMENT,
)

DEFAULT_ADDRESS = None
DEFAULT_TEXT_TO_SEND = "HELLO"
DEFAULT_JT = None
DEFAULT_DEVICE_NAME = "CoolLEDX"
DEFAULT_CONNECTION_TIMEOUT = 10.0
DEFAULT_CONNECTION_RETRIES = 5


def parse_standard_arguments() -> argparse.Namespace:
    """Parse standard command line arguments for the CoolLEDX driver."""
    parser = argparse.ArgumentParser(description="Commands to send to the sign.")
    parser.add_argument(
        "-a",
        "--address",
        help="MAC address of the sign",
        default=DEFAULT_ADDRESS,
        nargs="?",
    )
    parser.add_argument(
        "-d",
        "--device-name",
        help="Name of the device to connect to; defaults to CoolLEDX",
        default=DEFAULT_DEVICE_NAME,
        nargs="?",
    )
    parser.add_argument(
        "-t",
        "--text",
        help="Text to display",
        default=DEFAULT_TEXT_TO_SEND,
    )
    parser.add_argument(
        "-c",
        "--color",
        default=DEFAULT_COLOR,
        help="Color of the text as #rrggbb hex or a color name",
    )
    parser.add_argument('--size', '-s', choices=['small', 'large'], default='large',
        help="Taille : small (6x8, ~13 chars) ou large (10x14, ~8 chars). Défaut: large")
    parser.add_argument('--number', '-n', default=0, type=int,
        help="Numéro du pilote")
    parser.add_argument("-l", "--log", default=DEFAULT_LOGGING, help="Logging level")
    parser.add_argument(
        "--connection-timeout",
        type=float,
        default=DEFAULT_CONNECTION_TIMEOUT,
        help="Timeout in seconds for Bluetooth connection attempts (default: 10.0)",
    )
    parser.add_argument(
        "--connection-retries",
        type=int,
        default=DEFAULT_CONNECTION_RETRIES,
        help="Number of connection retry attempts (default: 5)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=int,
        default=DEFAULT_MODE,
        help="Mode of the scroller (1-8), or -1 to not touch",
    )
    parser.add_argument(
        "-w",
        "--width-treatment",
        type=str,
        default=DEFAULT_WIDTH_TREATMENT,
        help="Width treatment (scale/crop-pad/as-is)",
    )
    parser.add_argument(
        "-g",
        "--height-treatment",
        type=str,
        default=DEFAULT_HEIGHT_TREATMENT,
        help="Height treatment (scale/crop-pad)",
    )
    parser.add_argument(
        "-z",
        "--horizontal-alignment",
        type=str,
        default=DEFAULT_HORIZONTAL_ALIGNMENT,
        help="Horizontal alignment (left/center/right/none)",
    )
    parser.add_argument(
        "-y",
        "--vertical-alignment",
        type=str,
        default=DEFAULT_VERTICAL_ALIGNMENT,
        help="Vertical alignment (top/center/bottom)",
    )
    parser.add_argument(
        "-jt",
        "--jtfile",
        default=DEFAULT_JT,
        help="JT file to display",
    )
    return parser.parse_args()