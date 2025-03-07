#version 300 es
precision highp float;

uniform sampler2D Texture;
uniform sampler2D planetTexture;
uniform sampler2D planetNormalTexture;
uniform sampler2D planetUVTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

// https://www.shadertoy.com/view/XtjcRd
vec3 water() {
    float progress = time; //You can replace iTime with any variable that constantly increases
    float waveSize = 0.015f; //How extreme the wavyness is
    float ripple = 30.0f; //How "rippley" it is.
    float zoom = (waveSize * 3.0f) + 1.0f; // Zoom correction

    vec3 waterColor = vec3(0.0f, 0.07f, 0.25f);

    vec2 uv = fragCoord;

    //We offset the y by the x + progress
    uv.y -= sin(((progress * 0.1f) + uv.x) * ripple) * waveSize;

    //We do the reverse for x. I used cosine instead to make the uv.y and uv.x sync differently
    uv.x -= cos(((progress * 0.1f) + uv.y) * ripple) * waveSize;
    //To avoid glitchy borders from offsetting the texture
    //We need to zoom in a bit and re-center the texture.
    uv.xy /= vec2(zoom, zoom);
    uv.xy += vec2((zoom - 1.0f) / 2.0f, (zoom - 1.0f) / 2.0f);

    //Grab the rgb from our uv coord
    vec3 tex1 = texture(Texture, uv).bgr;

    return tex1 + waterColor * tex1 + vec3(0.001f) * (texture(planetTexture, vec2(0.0f, 0.0f)).bgr +
        texture(planetUVTexture, vec2(0.0f, 0.0f)).bgr +
        texture(planetNormalTexture, vec2(0.0f, 0.0f)).bgr);
}

void main() {

    vec3 final;
    if(fragCoord.y > 0.6f) {
        final = water();
    } else {
        final = texture(Texture, fragCoord).bgr;
    }

    fragColor = vec4(final, 1.0f);
}
