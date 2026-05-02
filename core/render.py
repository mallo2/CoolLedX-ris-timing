"""Rendering functions for the CoolLEDx sign."""

from __future__ import annotations

import json
import logging

from core import (
    DEFAULT_BACKGROUND_COLOR,
    HeightTreatment,
    HorizontalAlignment,
    VerticalAlignment,
    WidthTreatment,
)

LOGGER = logging.getLogger(__name__)

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
    render_as_image = False
    jt_rgb_data = None

    with open(filename) as f:
        jtf = f.read()
        jt = json.loads(jtf)[0]
    if "graffitiData" in list(jt["data"]):
        render_as_image = True
        jt_rgb_data = jt["data"]["graffitiData"]
    _sign_width = jt["data"]["pixelWidth"]
    _sign_height = jt["data"]["pixelHeight"]

    pixel_payload = bytearray()
    pixel_payload += bytearray(24)

    if jt_rgb_data is not None:
        pixel_bits_all = bytearray(jt_rgb_data)
        pixel_payload += len(pixel_bits_all).to_bytes(2, byteorder="big")
        pixel_payload += pixel_bits_all

    return pixel_payload, render_as_image