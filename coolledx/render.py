"""Rendering functions for the CoolLEDx sign."""

from __future__ import annotations

import json
import logging

from coolledx import (
    DEFAULT_BACKGROUND_COLOR,
    HeightTreatment,
    HorizontalAlignment,
    VerticalAlignment,
    WidthTreatment,
)

LOGGER = logging.getLogger(__name__)

# Constants
PIXELS_PER_BYTE = 8
MAX_TEXT_LENGTH = 255
COLOR_MARKER_COUNT = 2

def create_jt_payload(
    filename: str,
    _sign_width: int,
    _sign_height: int,
    _background_color: str = DEFAULT_BACKGROUND_COLOR,
    _width_treatment: WidthTreatment = WidthTreatment.LEFT_AS_IS,
    _height_treatment: HeightTreatment = HeightTreatment.CROP_PAD,
    _horizontal_alignment: HorizontalAlignment = HorizontalAlignment.NONE,
    _vertical_alignment: VerticalAlignment = VerticalAlignment.CENTER,
) -> tuple[bytearray, bool]:
    """Create JT payload from file for the sign."""
    #    im = Image.open(filename).convert("RGB")
    render_as_image = False  # Until proven otherwise . .
    frames = 1  # Until proven otherwise . .
    speed = 0  # Until proven otherwise . .
    jt_rgb_data = None  # Until proven otherwise . .

    with open(filename) as f:
        jtf = f.read()
        jt = json.loads(jtf)[0]  # json.loads(f)[0] JT data to dictionary
    if "aniData" in list(jt["data"]):
        jt_rgb_data = jt["data"]["aniData"]
        render_as_image = False
    if "graffitiData" in list(jt["data"]):
        render_as_image = True
        jt_rgb_data = jt["data"]["graffitiData"]
    # Unused - prefix with _ to suppress warning
    _sign_width = jt["data"]["pixelWidth"]
    _sign_height = jt["data"]["pixelHeight"]
    if "frameNum" in list(jt["data"]):
        frames = jt["data"]["frameNum"]
    if "delays" in list(jt["data"]):
        speed = jt["data"]["delays"]

    # create the image payload
    pixel_payload = bytearray()
    # unknown 24 zero-bytes
    pixel_payload += bytearray(24)
    # all the pixel-bits RGB
    # pixel_bits_all = bytearray().join([bR, bG, bB])

    # --------animation-------------------
    if not render_as_image:
        # number of frames
        pixel_payload += frames.to_bytes(1, byteorder="big")
        # speed (16-bit)
        pixel_payload += speed.to_bytes(2, byteorder="big")
    # --------animation-------------------

    if jt_rgb_data is not None:
        pixel_bits_all = bytearray(jt_rgb_data)
        # size of the pixel payload in its un-split form.
        pixel_payload += len(pixel_bits_all).to_bytes(2, byteorder="big")
        # all the pixel-bits
        pixel_payload += pixel_bits_all

    return pixel_payload, render_as_image
