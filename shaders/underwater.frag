#version 300 es
precision highp float;
uniform sampler2D Texture;
#include "uniforms"
in vec2 fragCoord;
out vec4 fragColor;

// Custom Shader Stuff

bool infinite = true;
float PI = 2.0 * asin(1.0);

struct WaveEmitter {
    vec2 mPosition;
    float mAmplitude;  // factor of final displacement
    float mVelocity;  // screens per second
    float mWavelength;  // screens
};

float GetPeriodTime(WaveEmitter waveEmitter) {
    return waveEmitter.mWavelength / waveEmitter.mVelocity;
}

float emitter_size = 3.0;
WaveEmitter emitter[3];

float GetPhase(vec2 point, WaveEmitter emit, float time) {
    float distance = sqrt(pow(point.x - emit.mPosition.x, 2.0) + pow(point.y - emit.mPosition.y, 2.0));
    if (!infinite && distance / emit.mVelocity >= time) {
        return 0.0;
    } else {
        return sin((time / GetPeriodTime(emit) - distance / emit.mWavelength) * 2.0 * PI);
    }
}

vec2 transformCoord(vec2 orig) {
    vec2 final = orig;
    for (int i = 0; i < int(emitter_size); ++i) {
        vec2 rel = orig - emitter[i].mPosition;
        float fac = GetPhase(orig, emitter[i], time) * emitter[i].mAmplitude;
        final += fac * rel;
    }
    return final;
}

vec4 transformColor(vec4 c, vec2 p) {
    float fac = 0.0;
    float a = 0.0;
    for (int i = 0; i < int(emitter_size); ++i) {
        fac += GetPhase(p, emitter[i], time) * emitter[i].mAmplitude;
        a = emitter[i].mAmplitude;
    }
    fac = (fac / a + 1.0) / 2.0;
    return c * fac;
}

void main() {
    WaveEmitter emit0;
    emit0.mPosition = vec2(0.1, 0.7);
    emit0.mAmplitude = 0.012;
    emit0.mVelocity = 0.06;
    emit0.mWavelength = 0.7;
    emitter[0] = emit0;

    WaveEmitter emit1;
    emit1.mPosition = vec2(0.8, -0.1);
    emit1.mAmplitude = 0.006;
    emit1.mVelocity = 0.07;
    emit1.mWavelength = 0.3;
    emitter[1] = emit1;

    WaveEmitter emit2;
    emit2.mPosition = vec2(1.1, 0.9);
    emit2.mAmplitude = 0.017;
    emit2.mVelocity = 0.05;
    emit2.mWavelength = 0.8;
    emitter[2] = emit2;

    vec2 coord = transformCoord(fragCoord);
    vec4 result = texture(Texture, coord);  // texture2D replaced with texture
    fragColor = result.bgra;  // Output color assignment
}