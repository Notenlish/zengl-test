import struct

_palette = [
    "FF5ba675",
    "FF6bc96c",
    "FFabdd64",
    "FFfcef8d",
    "FFffb879",
    "FFea6262",
    "FFcc425e",
    "FFa32858",
    "FF751756",
    "FF390947",
    "FF611851",
    "FF873555",
    "FFa6555f",
    "FFc97373",
    "FFf2ae99",
    "FFffc3f2",
    "FFee8fcb",
    "FFd46eb3",
    "FF873e84",
    "FF1f102a",
    "FF4a3052",
    "FF7b5480",
    "FFa6859f",
    "FFd9bdc8",
    "FFffffff",
    "FFaee2ff",
    "FF8db7ff",
    "FF6d80fa",
    "FF8465ec",
    "FF834dc4",
    "FF7d2da0",
    "FF4e187c",
]

# this gets run everytime theres a shader reload but you know what im too lazy
palette = []
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
        "bodyRadius": {
            "value": lambda: struct.pack("f", self.bodyRadius),
            "glsl_type": "float",
        },
        "screenResolution": {
            "value": lambda: struct.pack(
                "ff", self.screen_size[0], self.screen_size[1]
            ),
            "glsl_type": "vec2",
        },
        "aspectRatio": {
            "value": lambda: struct.pack("ff", 16, 9),
            "glsl_type": "vec2",
        },
        "lightDirection": {
            "value": lambda: struct.pack("fff", 0.3, 0.3, -1),
            "glsl_type": "vec3",
        },
        "palette": {
            "value": get_palette_buf,
            "glsl_type": "vec3[32]"
        }
    }
    return uniforms_map
