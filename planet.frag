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

// sphere projection:
// R being radius
// x^2 + y^2 + z^2 = R^2 


float getZSphere(float rad, float x, float y) {
    return sqrt(pow(rad, 2.0) - pow(x, 2.0) - pow(y, 2.0));
}

float getZSphere2(vec2 uv, float dis) {
    vec3 result = vec3(uv.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;
    return result.z;
}


void main() {
    vec2 pos = fragCoord * screenResolution;

    float dis = distance(vec2(screenResolution * 0.5), pos);
    if (dis <= bodyRadius) {
        vec2 pixellized_uv = floor(fragCoord * pixels) / pixels;
        
        vec2 uv_remap = pos - vec2(screenResolution * 0.5); // replace vec2(screenResolution * 0.5) with pos in future
        vec3 normal = vec3(uv_remap.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;

        // Normalize the normal vector
        normal = normalize(normal);
        
        // Calculate spherical coordinates
        float theta = acos(-normal.y);  // - to flip img
        float phi = atan(normal.z, -normal.x);

        // Convert spherical coordinates to texture coordinates
        float u = (phi + PI) / (2.0 * 3.141592653589793);
        float v = theta / 3.141592653589793;

        // Now u and v are the 2D UV coordinates for the planet texture
        vec2 texture_uv = vec2(u, v);
        // texture_uv.x += time;
        // texture_uv.x = mod(texture_uv.x, 1.0);

        /*
        // calculate light dist
        float d_light = distance(texture_uv, light_result);
        vec3 col = texture(planetTexture, texture_uv).bgr;

        if (d_light > 1.0) {
            col -= vec3(0.3);
        }
        */


        vec3 lightColor = vec3(1.0);
		float ringcount = 0.1001; // 1/ringcount
		float graincount = 128.0; // really its just totalGrainsInGrid
		float edge = 0.05; // must be less than 1/ringcount

        vec3 NotfragColor = texture(planetTexture, texture_uv).bgr * lightColor; //lightColor is a uniform vec3
		float ls = max(dot(normal, -normalize(lightDirection)), 0.04);
		if (mod(ls, ringcount) >= edge && ls < 0.899) {
		
			if ((mod(texture_uv.x*graincount, 2.0) < 1.0 && mod(texture_uv.y*graincount, 2.0) < 1.0) ||
				(mod(texture_uv.x*graincount, 2.0) > 1.0 && mod(texture_uv.y*graincount, 2.0) > 1.0)) {
				ls += 0.1001;
			}
		}
        NotfragColor = NotfragColor * max(ls - mod(ls, 0.1001), 0.04); //lightDirection is also a uniform
        //NotfragColor -= mod(NotfragColor, 0.1001); // floor to 0.1 w/out messin up center px, helpful when adding a pallete
        
        fragColor = vec4(NotfragColor, 1.0);
    } else {
        fragColor = texture(Texture, fragCoord).bgra;
    }
}
