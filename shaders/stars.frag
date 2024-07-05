#version 300 es
precision highp float;

uniform sampler2D Texture;
uniform sampler2D planetTexture;
uniform sampler2D planetNormalTexture;
uniform sampler2D planetUVTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;


vec3 stars() {
    // call this only for pure black backgrounds(space)

    // camera_pos will be an uniform
    vec2 cam_pos = cameraPos / vec2(1000000.0);
    vec2 uv = fragCoord / vec2(2.0) + vec2(1.0, 0.5) + cam_pos;
    uv = vec2(mod(uv.x, 1.0), mod(uv.y, 1.0));
    
    // dont use those hash13 things, it doesnt work, just make a really simple algorithm that colors it white if it fullfills an condition that is seemingly random
    // wait isnt that what perlin noise / hash13 is
    // bruh    
}

void main() {
    
    vec3 final = stars();
    

    fragColor = vec4(final, 1.0);
}
