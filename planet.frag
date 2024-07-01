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
        /*
        // Calculate 2D normalized coordinates
        vec2 uv = fragCoord;

        // Convert 2D normalized coordinates (uv) to spherical coordinates
        float phi = uv.x * 3.141592653589793 * 2.0;  // Azimuthal angle (0 to 2π)
        float theta = uv.y * 3.141592653589793;      // Polar angle (0 to π)

        // Convert spherical coordinates to 3D Cartesian coordinates
        vec3 spherePosition;
        spherePosition.x = -sin(phi);
        spherePosition.y = cos(theta);
        spherePosition.z = getZSphere2(uv, dis);

        // cos(phi) * cos(theta)  ==> lits up bottom part
        // sin(theta)  ==> nearly everywhere is lit up
        */

        /*
        // Convert spherical coordinates to Normal
        vec2 uv_remap = pos - vec2(screenResolution * 0.5); // replace vec2(screenResolution * 0.5) with pos in future
        vec3 normal = vec3(uv_remap.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;

        // Calculate the spherical coordinates
        float phi2 = atan(spherePosition.y, -spherePosition.x);
        float theta2 = acos(spherePosition.z);

        // Normalize phi to range [0, 1]
        float u = phi2 / (2.0 * 3.141592653589793);

        // Normalize theta to range [0, 1]
        float v = theta2 / 3.141592653589793;

        // Ensure UV coordinates are in the range [0, 1]
        if (u < 0.0) u += 1.0;
        if (v < 0.0) v += 1.0;

        // Now u and v are the 2D UV coordinates for the planet texture
        vec2 texture_uv = vec2(u, v);
        */
        
        
        
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


        vec3 lightColor = vec3(1.0, 1.0, 1.0);

        vec3 NotfragColor = vec4(texture(planetTexture, texture_uv).bgr, 1.0).rgb * lightColor; //lightColor is a uniform vec3
        NotfragColor = NotfragColor * max(dot(normal, -normalize(lightDirection)), 0.01); //lightDirection is also a uniform
        NotfragColor -= mod(NotfragColor, 0.1001); // floor to 0.1 w/out messin up center px
        // fragColor = vec4(NotfragColor, 1); 


        int grainSize = 128;

        // grain
        ivec2 pixelCoords = ivec2(pos.xy);
        ivec2 pixelFloordiv = pixelCoords - (pixelCoords%(grainSize*2));
        if ((pixelFloordiv.x < grainSize && pixelFloordiv.y < grainSize) || (pixelFloordiv.x > grainSize && pixelFloordiv.y > grainSize)) { // error here
            NotfragColor.rgb += vec3(0.1);
        }
        NotfragColor = clamp(NotfragColor, 0.0, 1.0);

        fragColor = vec4(NotfragColor, 1.0);

        // Example: Coloring based on the spherical coordinates
        // vec3 color = spherePosition * 0.5 + 0.5;  // Adjust to range [0,1]
        // vec3 color = vec3(spherePosition);
    } else {
        fragColor = texture(Texture, fragCoord).bgra;
    }
}