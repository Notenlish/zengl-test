import struct

_palette = """000000
21283f
38526e
3f86b0
839dbf
cee3ef
"""


# this gets run everytime theres a shader reload but you know what im too lazy
palette = []
_palette = _palette.splitlines()
palette_size = len(_palette)
for v in _palette:
    r, g, b = tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))
    rgb = (r / 255, g / 255, b / 255)
    palette.append(rgb)


def get_palette_buf():
    buffer = bytearray()
    for rgb in palette:
        buffer.extend(struct.pack("fff", *rgb))
    return buffer


def get_uniforms(self):
    uniforms_map = {
        "time": {
            "value": lambda: struct.pack("f", self.time_elapsed),
            "glsl_type": "float",
        },
        "planetCenter": {
            "value": lambda: struct.pack("ff", *self.planetPos),
            "glsl_type": "vec2",
        },
        "bodyRadius": {
            "value": lambda: struct.pack("f", self.bodyRadius),
            "glsl_type": "float",
        },
        "cloudRadius": {
            "value": lambda: struct.pack("f", self.cloudRadius),
            "glsl_type": "float",
        },
        "screenResolution": {
            "value": lambda: struct.pack(
                "ff", self.screen_size[0], self.screen_size[1]
            ),
            "glsl_type": "vec2",
        },
        "aspectRatio": {
            "value": lambda: struct.pack("f", 16 / 9),
            "glsl_type": "float",
        },
        "screenAspect": {
            "value": lambda: struct.pack("ff", 16, 9),
            "glsl_type": "vec2",
        },
        "lightDirection": {
            "value": lambda: struct.pack("fff", 0.3, 0.6, -1),
            "glsl_type": "vec3",
        },
        "paletteSize": {
            "value": lambda: struct.pack("i", palette_size),
            "glsl_type": "int",
        },
        "palette": {"value": get_palette_buf, "glsl_type": f"vec3[{palette_size}]"},
    }
    return uniforms_map
