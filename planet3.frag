#version 300 es
precision highp float;
precision highp int;

uniform sampler2D Texture;  // pygame surface passed to the gpu.
uniform sampler2D planetTexture;
uniform sampler2D planetNormalTexture;
uniform sampler2D planetUVTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;

bool shouldPixellize = false;
bool shouldDoLighting = true;
bool shouldDither = true;

float PI = 3.1415926535897932384626433832795;
vec2 light_origin = vec2(0.7, 0.5);
float pixelSize = 8.0;

// Planet Gen Godot Parameters //
float size = 25.0;  // controls fbm size + rand function // 40 - 200
float seed = 3.4;
int OCTAVES = 2;  // between 2 - 20

float rand(vec2 coord) {
	coord = mod(coord, vec2(1.0, 1.0)*round(size));
	return fract(sin(dot(coord.xy ,vec2(12.9898,78.233))) * 15.5453 * seed);
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

float fbm(vec2 coord){
	float value = 0.0;
	float scale = 0.5;

	for (int i = 0; i < OCTAVES ; i++){
		value += noise(coord) * scale;
		coord *= 2.0;
		scale *= 0.5;
	}
	return value;
}

float getZSphere(float rad, float x, float y) {
    return sqrt(pow(rad, 2.0) - pow(x, 2.0) - pow(y, 2.0));
}

float getZSphere2(vec2 uv, float dis) {
    vec3 result = vec3(uv.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;
    return result.z;
}

vec2 pixellize(vec2 uv) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}

vec2 rotate_uv(vec2 uv, float rotation)
{
    float cosAngle = cos(rotation);
    float sinAngle = sin(rotation);
    vec2 p = uv - vec2(0.5);
    return vec2(
        cosAngle * p.x + sinAngle * p.y + 0.5,
        cosAngle * p.y - sinAngle * p.x + 0.5
    );
}


vec2 texture_uv_sphere(vec3 normal) {
    float theta = acos(-normal.y);  // - to flip img vertically
    float phi = atan(normal.z, -normal.x);

    // Convert spherical coordinates to texture coordinates
    float u = (phi + PI) / (2.0 * 3.141592653589793);
    float v = theta / 3.141592653589793;

    // Now u and v are the 2D UV coordinates for the planet texture
    return vec2(u, v);
}

float cloud(vec2 texture_uv) {
    float fbm1 = fbm(texture_uv * vec2(100.0));
    float fbm_val = fbm(texture_uv * size+fbm1+vec2(time*time_speed, 0.0));
    return mod(fbm_val, 1.0);
}

vec3 normal_sphere(vec2 uv_remap, float dis) {
    vec3 normal = vec3(uv_remap.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;
    normal = normalize(normal);
    normal.z = clamp(normal.z, 0.1, 1.0);  // gets rid of weird jagged pixels
    return normal;
}

vec3 lighting(vec2 texture_uv, vec3 normal ) {
    vec3 lightColor = vec3(1.0);
    float ringcount = 0.2001; // 1/ringcount
    float graincount = 128.0; // really its just totalGrainsInGrid
    float edge = 0.05; // must be less than 1/ringcount

    float fbm1 = fbm(texture_uv);
    // maybe move time*time_speed to py and send as uniform?
    float fbm_val = fbm(texture_uv * size + fbm1 + vec2(time*time_speed, 0.0)) * 0.3;

    vec3 NotfragColor = texture(planetTexture, texture_uv).bgr * lightColor; //lightColor is a uniform vec3
    float ls = max(dot(normal, -normalize(movedLightDirection)), 0.04); // luminosity
    
    ls -= fbm_val;  // apply fbm
    
    if (mod(ls, ringcount) >= edge && ls < 0.899) {
        if ((mod(texture_uv.x*graincount, 2.0) < 1.0 && mod(texture_uv.y*graincount, 2.0) < 1.0) ||
            (mod(texture_uv.x*graincount, 2.0) > 1.0 && mod(texture_uv.y*graincount, 2.0) > 1.0)) {
            ls += 0.1001;
        }
    }
    vec3 result;
    if (shouldDoLighting) {
        result = NotfragColor * (1.0 * max(ls - mod(ls, 0.1001), 0.04)); //lightDirection is also a uniform
    }
    else {
        result = NotfragColor; 
    }
    return result;
}

vec3 lighting2(vec2 texture_uv, vec3 normal) {
    vec3 lightColor = vec3(1.0);
    float ringcount = 0.2001; // 1/ringcount
    float graincount = 128.0; // really its just totalGrainsInGrid
    float edge = 0.05; // must be less than 1/ringcount

    float fbm1 = fbm(texture_uv);
    // maybe move time*time_speed to py and send as uniform?
    float fbm_val = fbm(texture_uv * size + fbm1 + vec2(time*time_speed, 0.0)) * 0.3;

    float ls = max(dot(normal, -normalize(movedLightDirection)), 0.04); // luminosity
    ls -= fbm_val;
    
    // dithering
    if (shouldDither && mod(ls, ringcount) >= edge && ls < 0.899) {
        if ((mod(texture_uv.x*graincount, 2.0) < 1.0 && mod(texture_uv.y*graincount, 2.0) < 1.0) ||
            (mod(texture_uv.x*graincount, 2.0) > 1.0 && mod(texture_uv.y*graincount, 2.0) > 1.0)) {
            ls += 0.1001;
        }
    }

    vec3 col;
    if (ls >= 0.9) {
        col = palette[1].rgb;
    } else if (ls >= 0.7) {
        col = palette[2].rgb;
    } else {
        // make it not complain
        texture(planetTexture, vec2(0.0,0.0));
        col = palette[3].rgb;
    }
    return col;
}

void main() {
    vec2 pos = fragCoord * screenResolution;

    float dis = distance(planetCenter, pos);
    
    if (dis < bodyRadius) {


        vec2 uv_remap = pos - planetCenter;
        vec3 normal = normal_sphere(uv_remap, dis);

        vec2 texture_uv = texture_uv_sphere(normal);

        // for this to work you need to use "wrap_x":"repeat" in the texture settings
        texture_uv.x += planetOffset;

        if (shouldPixellize == true) {
            texture_uv = pixellize(texture_uv);
        }

        float cloud_val = cloud(texture_uv);
        float isCloud = step(cloud_val, 0.35);

        vec3 col = lighting(texture_uv, normal); //+ vec3(1.0) * isCloud;

        fragColor = vec4(col, 1.0);
        
    } else {
        vec3 c1 = texture(planetNormalTexture, vec2(0.0,0.0)).bgr;
        vec3 c2 = texture(planetUVTexture, vec2(0.0,0.0)).bgr;
        vec3 c3 = texture(Texture, fragCoord).bgr;
        fragColor = vec4(c3 * vec3(0.99) + (c2+c1)*vec3(0.01), 1.0);
    }
    
}
