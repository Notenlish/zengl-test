#version 300 es
precision highp float;

uniform sampler2D Texture;  // pygame surface passed to the gpu.

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;


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
        float z = getZSphere(bodyRadius, pos.x, pos.y);

        //////////////////////
        
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

        // Example: Coloring based on the spherical coordinates
        // vec3 color = spherePosition * 0.5 + 0.5;  // Adjust to range [0,1]
        vec3 color = vec3(spherePosition);
        fragColor = vec4(color, 1.0);
    } else {
        fragColor = texture(Texture, fragCoord).bgra;
    }
}