#version 300 es
precision highp float;
precision highp int;

uniform sampler2D Texture;
uniform sampler2D planetTexture;
uniform sampler2D planetNormalTexture;
uniform sampler2D planetUVTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

bool shouldPixellize = false;
bool shouldDither = true;

vec3 cloudColor = vec3(1.0);
vec3 lightColor = vec3(1.0);

const float PI = 3.1415926535897932384626433832795;
const vec2 light_origin = vec2(0.7, 0.5);
const float pixelSize = 8.0;

// Planet Gen Godot Parameters
const float size = 25.0;
const float seed = 3.4;
const int OCTAVES = 2;

float rand(vec2 coord) {
    coord = mod(coord, vec2(1.0) * round(size));
    return fract(sin(dot(coord.xy, vec2(12.9898, 78.233))) * 15.5453 * seed);
}

float noise(vec2 coord) {
    vec2 i = floor(coord);
    vec2 f = fract(coord);
    
    float a = rand(i);
    float b = rand(i + vec2(1.0, 0.0));
    float c = rand(i + vec2(0.0, 1.0));
    float d = rand(i + vec2(1.0, 1.0));

    vec2 cubic = f * f * (3.0 - 2.0 * f);

    return mix(a, b, cubic.x) + (c - a) * cubic.y * (1.0 - cubic.x) + (d - b) * cubic.x * cubic.y;
}

float fbm(vec2 coord) {
    float value = 0.0;
    float scale = 0.5;

    for (int i = 0; i < OCTAVES; i++) {
        value += noise(coord) * scale;
        coord *= 2.0;
        scale *= 0.5;
    }
    return coord.x;
}

vec2 pixellize(vec2 uv) {
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}

float cloud(vec2 texture_uv) {
    float fbm1 = fbm(texture_uv * vec2(100.0));
    float fbm_val = fbm(texture_uv * size + fbm1 + vec2(time * time_speed, 0.0));
    return mod(fbm_val, 1.0);
}

vec2 LightandDither(vec3 normal, vec2 texture_uv) {
    const float ringcount = 0.2001;
    const float graincount = 128.0;
    const float edge = 0.05;

    float fbm1 = fbm(texture_uv);
    float fbm_val = fbm(texture_uv * size + fbm1 + vec2(time * time_speed, 0.0)) * 0.3;
    
    float ls = max(dot(normal, -normalize(movedLightDirection)), 0.04);
    ls -= fbm_val;

    float dithered_ls = ls;
    if (mod(ls, ringcount) >= edge && ls < 0.899) {
        if ((mod(texture_uv.x * graincount, 2.0) < 1.0 && mod(texture_uv.y * graincount, 2.0) < 1.0) ||
            (mod(texture_uv.x * graincount, 2.0) > 1.0 && mod(texture_uv.y * graincount, 2.0) > 1.0)) {
            dithered_ls += 0.1001;
        }
    }

    return vec2(ls, dithered_ls);
}

vec3 cloudFinal(float ls, vec2 texture_uv) {
    vec3 nodither_shadow_mul = vec3(1.0 * max(ls - mod(ls, 0.1001), 0.04));
    vec3 NotfragColor = texture(planetTexture, texture_uv).bgr * lightColor;
    vec3 cloud_result = cloudColor * nodither_shadow_mul;
    vec3 result = !isStar ? cloud_result + vec3(0.1) : NotfragColor;
    return result;
}

vec3 planetFinal(float dithered_ls, vec2 texture_uv) {
    vec3 NotfragColor = texture(planetTexture, texture_uv).bgr * lightColor;
    vec3 dithered_shadow_mul = vec3(1.0 * max(dithered_ls - mod(dithered_ls, 0.1001), 0.04));
    vec3 planet_result = vec3(1.5) * NotfragColor * dithered_shadow_mul;
    vec3 result = !isStar ? planet_result : NotfragColor;
    return result;
}

void main() {
    vec2 pos = fragCoord * screenResolution;
    float dis = distance(planetCenter, pos);

    if (dis <= cloudRadius) {
        vec2 uv_remap = (pos - planetCenter) / (cloudRadius * 2.0) + 0.5;
        vec3 normal = texture(planetNormalTexture, uv_remap * vec2(1, -1)).bgr;
        vec2 texture_uv = texture(planetUVTexture, uv_remap * vec2(1, -1)).bg;
        texture_uv.x += planetOffset;

        if (shouldPixellize) {
            texture_uv = pixellize(texture_uv);
        }

        float cloud_val = cloud(texture_uv);
        float isCloud = step(cloud_val, 0.35);
        vec2 ld = LightandDither(normal, texture_uv);

        if (isCloud == 1.0) {
            fragColor = vec4(cloudFinal(ld.x, texture_uv), 1.0);
        } else if (dis <= bodyRadius) {
            uv_remap = (pos - planetCenter) / (bodyRadius * 2.0) + 0.5;
            normal = texture(planetNormalTexture, uv_remap * vec2(1, -1)).bgr;
            texture_uv = texture(planetUVTexture, uv_remap * vec2(1, -1)).bg;
            texture_uv.x += planetOffset;
            if (shouldPixellize) {
                texture_uv = pixellize(texture_uv);
            }
            fragColor = vec4(planetFinal(ld.y, texture_uv), 1.0);
        } else {
            fragColor = texture(Texture, fragCoord).bgra;
        }
    } else {
        fragColor = texture(Texture, fragCoord).bgra;
    }
}
