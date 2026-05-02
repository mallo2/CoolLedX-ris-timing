import json

def create_jt_payload(
    filename: str,
    _background_color: str = "black",
    _width_treatment: str = "as-is",
    _height_treatment: str = "crop-pad",
    _horizontal_alignment: str = "none",
    _vertical_alignment: str = "center",
) -> bytearray:
    jt_rgb_data = None

    with open(filename) as f:
        jtf = f.read()
        jt = json.loads(jtf)[0]
    if "graffitiData" in list(jt["data"]):
        jt_rgb_data = jt["data"]["graffitiData"]

    pixel_payload = bytearray()
    pixel_payload += bytearray(24)

    if jt_rgb_data is not None:
        pixel_bits_all = bytearray(jt_rgb_data)
        pixel_payload += len(pixel_bits_all).to_bytes(2, byteorder="big")
        pixel_payload += pixel_bits_all

    return pixel_payload