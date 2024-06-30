#version 300 es
precision highp float;

uniform sampler2D Texture;  // pygame surface passed to the gpu.
uniform sampler2D planetTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

float PI = 3.1415926535897932384626433832795;


// sphere projection:
// R being radius
// x^2 + y^2 + z^2 = R^2 

float getZSphere2(vec2 uv, float dis) {
    vec3 result = vec3(uv.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;
    return result.z;
}


float pixels = 500.0; // 10.0 - 200.0 ig
float rotation = 1.0; // between 0.0, 6.28(2pi)
vec2 light_origin = vec2(0.39, 0.39);
float time_speed = 0.2;
float dither_size = 2.0;
float light_border_1 = 0.4;
float light_border_2 = 0.6;
float size = 50.0;
int OCTAVES = 16;
float seed = 2.4;
bool should_dither = true;


float rand(vec2 coord) {
	coord = mod(coord, vec2(1.0,1.0)*round(size));
	return fract(sin(dot(coord.xy ,vec2(12.9898,78.233))) * 15.5453 * seed);
}

vec2 rotate(vec2 coord, float angle){
	coord -= 0.5;
	coord *= mat2(vec2(cos(angle),-sin(angle)),vec2(sin(angle),cos(angle)));
	return coord + 0.5;
}

bool dither(vec2 uv1, vec2 uv2) {
	return mod(uv1.x+uv2.y,2.0/pixels) <= 1.0 / pixels;
}

float noise(vec2 coord){
	vec2 i = floor(coord);
	vec2 f = fract(coord);
	
	float a = rand(i);
	float b = rand(i + vec2(1.0, 0.0));
	float c = rand(i + vec2(0.0, 1.0));
	float d = rand(i + vec2(1.0, 1.0));

	vec2 cubic = f * f * (3.0 - 2.0 * f);

	return mix(a, b, cubic.x) + (c - a) * cubic.y * (1.0 - cubic.x) + (d - b) * cubic.x * cubic.y;
}

// fractional brownian motion
float fbm(vec2 coord){
    float value = 0.0;
    float scale = 0.5;

    for(int i = 0; i < OCTAVES ; i++){
        value += noise(coord) * scale;
        coord *= 2.0;
        scale *= 0.5;
    }
    return value;
}

void main() {
    vec4 colors[3];
    colors[0] = vec4(0.64, 0.65, 0.76, 1.0);
    colors[1] = vec4(0.26, 0.39, 0.53, 1.0);
    colors[2] = vec4(0.23, 0.25, 0.37, 1.0);

    vec2 pos = fragCoord * screenResolution;

    float dis = distance(vec2(screenResolution * 0.5), pos);
    if (dis <= bodyRadius) {
        // scaling uv to pixels and then flooring it basically rounds it to pixel grid, then you divide it back.
        vec2 uv = floor(fragCoord * pixels) / pixels;

        // check distance from center & distance to light
        float d_circle = distance(uv, vec2(0.5));
        float d_light = distance(uv , vec2(light_origin));
        // cut out a circle
        
        // if bigger than 0.4999, return 1 else return 0  ==> for pixel lighting
        // stepping over 0.5 instead of 0.49999 makes some pixels a little buggy
        float a = step(d_circle, 0.49999);

        bool dith = dither(uv, fragCoord);
        uv = rotate(uv, rotation);

        // get a noise value with light distance added
        // this creates a moving dynamic shape
        float fbm1 = fbm(uv);
        d_light += fbm(uv * size + fbm1 + vec2(time*time_speed, 0.0))*0.3; // change the magic 0.3 here for different light strengths
        
        // size of edge in which colors should be dithered
        float dither_border = (1.0/pixels)*dither_size;

        // now we can assign colors based on distance to light origin
        vec4 col = colors[0];
        if (d_light > light_border_1) {
            col = colors[1];
            if (d_light < light_border_1 + dither_border && (dith || !should_dither)) {
                col = colors[0];
            }
        }
        if (d_light > light_border_2) {
            col = colors[2];
            if (d_light < light_border_2 + dither_border && (dith || !should_dither)) {
                col = colors[1];
            }
        }
        
        fragColor = vec4(col.r, col.g, col.b, a * col.a);
        

    } else {
        fragColor = vec4(texture(Texture, fragCoord).bgra);
    }
    if (fragCoord.x > 1.0) {
        fragColor = texture(planetTexture, fragCoord).bgra;
    }
}