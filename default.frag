#version 300 es
precision highp float;

uniform sampler2D Texture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

void main() {
    vec4 color = texture(Texture, fragCoord).bgra;
    fragColor = color;
}
