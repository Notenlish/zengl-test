#version 300 es
precision highp float;

uniform sampler2D Texture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

// Custom Shader stuff

void main() {
    // Calculate the coordinates of the fragment relative to the center of the screen
    vec2 center = DDD * 0.5;
    vec2 fragCoord = gl_FragCoord.xy;
    vec2 position = (fragCoord - center) / DDD;

    // Calculate the distance from the center of the screen
    float distanceFromCenter = length(position);

    // If the distance is less than the radius, draw the circle
    if (distanceFromCenter < bodyRadius) {
        fragColor = vec4(1.0, 1.0, 1.0, 1.0); // White color
    } else {
        fragColor = vec4(0.0, 0.0, 0.0, 0.0); // Transparent
    }
}
