from enum import IntEnum, StrEnum

__version__ = "0.0.1"


class Mode(IntEnum):

    STATIC = 0x01
    LEFT = 0x02
    RIGHT = 0x03
    UP = 0x04
    DOWN = 0x05
    SNOWFLAKE = 0x06
    PICTURE = 0x07
    LASER = 0x08


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

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    NONE = "none"


class VerticalAlignment(StrEnum):

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


DEFAULT_COLOR = "white"
DEFAULT_BACKGROUND_COLOR = "black"

DEFAULT_LOGGING = "INFO"
DEFAULT_WIDTH_TREATMENT = WidthTreatment.LEFT_AS_IS
DEFAULT_HEIGHT_TREATMENT = HeightTreatment.CROP_PAD
DEFAULT_HORIZONTAL_ALIGNMENT = HorizontalAlignment.NONE
DEFAULT_VERTICAL_ALIGNMENT = VerticalAlignment.CENTER
