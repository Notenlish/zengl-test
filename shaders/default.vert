#version 300 es
precision highp float;

#include "uniforms"

vec2 vertex[4] = vec2[](
    vec2(-1.0, -1.0),
    vec2(-1.0, 1.0),
    vec2(1.0, -1.0),
    vec2(1.0, 1.0)
);

out vec2 fragCoord;

void main() {
    fragCoord = vertex[gl_VertexID] * vec2(0.5, -0.5) + 0.5;
    gl_Position = vec4(vertex[gl_VertexID], 0.5, 1.0);
}