import struct
import math
from copy import deepcopy
import webcolors

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from renderer import Renderer

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
    rgb = webcolors.hex_to_rgb(v if v[0]=="#" else f"#{v}")
    color = [rgb.red / 255, rgb.green / 255, rgb.blue / 255, 1.0]  # rgba
    palette.append(color)
# print(palette)

def set_speeds(self):
    self.time_speed = 1.0
    self.planetRotationSpeed = 0.01
    self.lightSpeed = 0.5


def get_palette_buf():
    buffer = bytearray()
    for rgb in palette:
        buffer.extend(struct.pack("ffff", *rgb))
    return buffer


def get_light_moved(self, renderer: "Renderer"):
    startLightRot = 0.0
    rot = startLightRot + (self.time_elapsed * renderer.light_speed)  # between 0 and 2pi
    rot %= 2.0 * math.pi
    offset = (math.sin(rot) * 2.0, math.cos(rot) * 2.0)

    newLightDirection = deepcopy(renderer.lightDirection)
    if renderer.shouldMoveLight:
        newLightDirection[0] += offset[0]
        newLightDirection[2] += offset[1]

    return newLightDirection


def get_planet_offset(self):
    # moves the planet(texture uv)
    return self.time_elapsed * self.time_speed * self.planetRotationSpeed

# self = app
def get_uniforms(self, renderer: "Renderer"):
    set_speeds(self)
    uniforms_map = {
        "time": {
            "value": lambda: struct.pack("f", self.time_elapsed),
            "glsl_type": "float",
        },
        "planetCenter": {
            "value": lambda: struct.pack("ff", *renderer.planetPos),
            "glsl_type": "vec2",
        },
        "bodyRadius": {
            "value": lambda: struct.pack("f", renderer.bodyRadius),
            "glsl_type": "float",
        },
        "cloudRadius": {
            "value": lambda: struct.pack("f", renderer.cloudRadius),
            "glsl_type": "float",
        },
        "screenResolution": {
            "value": lambda: struct.pack(
                "ff", 640.0, 480.0
            ),
            "glsl_type": "vec2",
        },
        "aspectRatio": {
            "value": lambda: struct.pack("f", 3 / 2),
            "glsl_type": "float",
        },
        "screenAspect": {
            "value": lambda: struct.pack("ff", 3, 2),
            "glsl_type": "vec2",
        },
        "lightDirection": {
            "value": lambda: struct.pack("fff", *renderer.lightDirection),
            "glsl_type": "vec3",
        },
        "movedLightDirection": {
            "value": lambda: struct.pack("fff", *get_light_moved(self, renderer)),
            "glsl_type": "vec3",
        },
        "paletteSize": {
            "value": lambda: struct.pack("i", palette_size),
            "glsl_type": "int",
        },
        "palette": {"value": get_palette_buf, "glsl_type": f"vec4[{palette_size}]"},
        "time_speed": {
            "value": lambda: struct.pack("f", self.time_speed),
            "glsl_type": "float",
        },
        "planetRotationSpeed": {
            "value": lambda: struct.pack("f", self.planetRotationSpeed),
            "glsl_type": "float",
        },
        "planetOffset": {
            "value": lambda: struct.pack("f", get_planet_offset(self)),
            "glsl_type": "float",
        },
        "isStar": {
            "value": lambda: struct.pack("?", renderer.isStar),
            "glsl_type":"bool"
        }
    }
    return uniforms_map
