import struct


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
    }
    return uniforms_map
