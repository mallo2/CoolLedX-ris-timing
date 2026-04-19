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
    """Parse standard command line arguments for the CoolLEDX driver."""
    parser = argparse.ArgumentParser(description="Commands to send to the sign.")
    parser.add_argument(
        "-a",
        "--address",
        help="MAC address of the sign",
        default=None,
        nargs="?",
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
        "-m",
        "--mode",
        type=int,
        default=DEFAULT_MODE,
        help="Mode of the scroller (1-8), or -1 to not touch",
    )
    return parser.parse_args()
