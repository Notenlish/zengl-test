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

    // you know what
    // I think we should draw the stars from the cpu
    // thats it, im gone
    return vec3(0.0);
}

void main() {
    
    // vec3 final = stars();
    vec3 no_complain = texture(Texture, vec2(0.0,0.0)).rgb + texture(planetTexture, vec2(0.0,0.0)).rgb + texture(planetNormalTexture, vec2(0.0,0.0)).rgb + texture(planetUVTexture, vec2(0.0,0.0)).rgb;
    

    fragColor = vec4(no_complain, 1.0);
}
