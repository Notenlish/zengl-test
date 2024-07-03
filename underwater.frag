#version 300 es
precision highp float;

uniform sampler2D Texture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

vec2 pixellize(vec2 uv, float pixelSize) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}

void main() {
    vec4 color = texture(Texture, pixellize(fragCoord * vec2(1, -1), 2.0)).rgba;
    fragColor = color;
}
