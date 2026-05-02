"""CoolLEDX driver package."""

from enum import StrEnum

__version__ = "0.0.1"

__all__: list[str] = [
    "HeightTreatment",
    "WidthTreatment",
    "HorizontalAlignment",
    "VerticalAlignment",
    "DEFAULT_BACKGROUND_COLOR"
]

class HeightTreatment(StrEnum):
    """
    Height needs to be, in the end, the sign's height, which is always a multiple
    of 8.  For the height, we can either scale it to the sign's height, or crop/pad it
    to the sign's height.
    """

    SCALE = "scale"
    CROP_PAD = "crop-pad"


class WidthTreatment(StrEnum):
    """
    Width can either be scaled to the sign's width, left as-is, or cropped/padded
    to the sign's width.
    """

    SCALE = "scale"
    CROP_PAD = "crop-pad"
    LEFT_AS_IS = "as-is"


class HorizontalAlignment(StrEnum):
    """Horizontal alignment of text/image on the sign."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    NONE = "none"


class VerticalAlignment(StrEnum):
    """Vertical alignment of text/image on the sign."""

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


DEFAULT_BACKGROUND_COLOR = "black"
