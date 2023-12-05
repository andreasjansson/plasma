# Plasma

_Plasma shader generator_

[https://replicate.com/andreasjansson/plasma](![Run on Replicate](https://replicate.com/andreasjansson/plasma/badge))

![screenshot](https://tjzk.replicate.delivery/models_models_cover_image/4754cd33-9599-4fde-88ab-b4498c610253/cap.gif)

This model uses CodeLlama 7B-instruct with Llama.cpp grammars to generate equations that create plasma shader effects. Refer to the source code for the full grammar and prompt.

Take the generated `effect()` function and replace the `effect()` function in the snippet below. Then copy the whole code snippet into https://www.shadertoy.com/new and hit ▶Compile.

```c
float resolution = 3.0;
float speed = 0.1;
int depth = 4;

vec3 color1 = vec3(235.0/255.0, 231.0/255.0, 92.0/255.0);
vec3 color2 = vec3(223.0/255.0, 72.0/255.0, 67.0/255.0);
vec3 color3 = vec3(235.0/255.0, 64.0/255.0, 240.0/255.0);

// Replace this with the generated effect() function
vec2 effect(vec2 p, float i, float time) {
  return vec2(cos(i * sin(p.x * p.y) + time), sin(length(p.y - p.x) * i + time));
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (2.0 * gl_FragCoord.xy - iResolution.xy) / max(iResolution.x, iResolution.y);
    p *= float(resolution);
    for (int i = 1; i < depth; i++) {
        float fi = float(i);
        p += effect(p, fi, iTime * float(speed));
    }
    vec3 col = mix(mix(color1, color2, 1.0-sin(p.x)), color3, cos(p.y+p.x));
    fragColor = vec4(col, 1.0);
}
```
