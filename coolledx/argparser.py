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


def parse_standard_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Commands to send to the sign.")
    parser.add_argument(
        "-a",
        "--address",
        help="MAC address of the sign",
        nargs="?",
    )
    parser.add_argument(
        "-c",
        "--color",
        default=DEFAULT_COLOR,
        help="Color of the text as #rrggbb hex or a color name",
    )
    parser.add_argument("-l", "--log", default=DEFAULT_LOGGING, help="Logging level")
    parser.add_argument(
        "-m",
        "--mode",
        type=int,
        default=DEFAULT_MODE,
    )
    return parser.parse_args()
