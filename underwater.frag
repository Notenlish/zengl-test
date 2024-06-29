#version 330 core
precision highp float;

uniform sampler2D Texture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

void main() {
    // Sample the texture at the fragment's coordinates
    vec4 texColor = texture(Texture, fragCoord).bgra;

    // Calculate a simple distortion effect using sine function
    float distortion = sin(fragCoord.y * 0.1 + time) * 0.1;

    // Apply distortion to fragment's coordinates
    vec2 distortedCoord = fragCoord + vec2(0.0, distortion);

    // Sample the texture using the distorted coordinates
    vec4 distortedColor = texture(Texture, distortedCoord);

    // Mix original color and distorted color
    fragColor = mix(texColor, distortedColor, 0.5);
}