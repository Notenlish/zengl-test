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
	vec2 scalling_factor = vec2(1.0, 0.843);
	float pixel_size = 2.0; // ig this should be good
	
    vec4 color = texture(Texture, pixellize(fragCoord * scalling_factor * vec2(1, -1), pixel_size)).rgba;
    fragColor = color;
}
