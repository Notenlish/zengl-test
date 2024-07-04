#version 300 es
precision highp float;

uniform sampler2D Texture;  // pygame surface passed to the gpu.
uniform sampler2D planetTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

float PI = 3.1415926535897932384626433832795;
vec2 light_origin = vec2(0.7, 0.5);
float pixels = 250.0;


float luminosity(vec3 color) {
    return dot(color, vec3(0.2126, 0.7152, 0.0722));
}

// find closest color from the palette
vec3 get_closest(vec3 col, float lum) {
    vec3 closestColor = vec3(0.0);
    float lowest = 100.0;

    for (int i=0; i < int(paletteSize); i++) {
        float paletteLum = luminosity(palette[i]);
        float lumDifference = abs(lum - paletteLum);
        float diff = length(col - palette[i]) + lumDifference;
        if (lowest > diff) {
            lowest = diff;
            closestColor = palette[i];
        }
    }
    return closestColor;
}



void main() {
    vec3 oldPixel = texture(Texture, fragCoord).bgr;
    vec3 newPixel = get_closest(oldPixel, luminosity(oldPixel));
    if (fragCoord.x > 1.0) {
        newPixel = texture(planetTexture, vec2(0.0,0.0)).bgr;
    }
    fragColor = vec4(newPixel, 1.0);
}