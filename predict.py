import os
import time
import subprocess
import json
import numpy as np
from cog import BasePredictor, Input, Path, BaseModel, ConcatenateIterator
import pprint as pp
from llama_cpp import LlamaGrammar, Llama


PROMPT = """<s>[INST]Below is an example of a ShaderToy "plasma" shader:

vec3 color1 = vec3(235.0/255.0, 231.0/255.0, 92.0/255.0);  // #EBE75C
vec3 color2 = vec3(223.0/255.0, 72.0/255.0, 67.0/255.0);   // #DF4843
vec3 color3 = vec3(235.0/255.0, 64.0/255.0, 240.0/255.0);  // #EB40F0

vec2 effect(vec2 p, float i, float time) {
    return vec2(cos(p.x * i + time), sin(p.y * i + time)) * vec2(sin(length(p) * i + time), cos(length(p) * i - time)) / i;
}


void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 p = (2.0 * fragCoord.xy - iResolution.xy) / max(iResolution.x, iResolution.y);
    p *= 5.0;
    for (int i = 1; i < 5; i++) {
        float fi = float(i);
        p += effect(p, fi, iTime*.5);
    }
    vec3 col = mix(mix(color1, color2, 1.0-sin(p.x)), color3, cos(p.y+p.x));
    fragColor = vec4(col, 1.0);
}

---

The "effect" function defines how the plasma is generated. Below are a few examples of "effect" functions:

// Basic Sine Wave

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(p.x * i + time), cos(p.y * i + time));
}

// Cosine Length Wave

vec2 effect(vec2 p, float i, float time) {
    return vec2(cos(length(p) * i + time), sin(length(p) * i + time));
}

// Sinusoidal Interference

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(p.x * i + time) * cos(p.y * i + time), cos(p.x * i + time) * sin(p.y * i + time));
}

// Expanding Ripple

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(length(p) * i + time) / i, cos(length(p) * i + time) / i);
}

// Rotational Distortion

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(i * (p.x + p.y) + time), cos(i * (p.x - p.y) + time));
}

// Circular Motion

vec2 effect(vec2 p, float i, float time) {
    return vec2(cos(length(p) * i + time), sin(length(p) * i + time)) / i;
}

// Sinusoidal Mirror

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(p.x * i + time) / i, cos(p.x * i + time) / i);
}

// Radial Pulsation

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(length(p) * i + time), cos(length(p) * i + time));
}

// Twisting Spiral

vec2 effect(vec2 p, float i, float time) {
    return vec2(cos(i * atan(p.y, p.x) + time), sin(i * atan(p.y, p.x) + time));
}

// Dynamic Harmonics

vec2 effect(vec2 p, float i, float time) {
    return vec2(cos(p.x * i + time), sin(p.y * i + time)) * vec2(sin(length(p) * i + time), cos(length(p) * i - time)) / i;
}

// Asymetric ripple

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(length(p) * i + time) / (i + 0.3), cos(length(p) * i + time) / (i + 0.7));
}

// Rotational twist

vec2 effect(vec2 p, float i, float time) {
    return vec2(cos(i * (p.x + 0.4) + time), sin(i * (p.y - 0.3) + time));
}

// Elliptical orbit

vec2 effect(vec2 p, float i, float time) {
    return vec2(sin(length(p) * 0.5 * i + time), cos(length(p) * 2.0 * i + time)) / i;
}

---

Generate a new effect function.[/INST]"""


GRAMMAR = """root ::= "vec2 effect(vec2 p, float i, float time) {\n  " return-statement "\n}"
return-statement ::= "return " vec2-expression ";"
vec2-expression ::= single-vec2-expression | single-vec2-expression operation vec2-expression
single-vec2-expression ::= "vec2(" scalar-expression ", " scalar-expression ")"
scalar-expression ::= single-scalar-expression | single-scalar-expression operation scalar-expression
single-scalar-expression ::= float-literal | variable | math-func "(" math-arg ")"
operation ::= " + " | " - " | " * " | " / "
math-func ::= "sin" | "cos" | "tan" | "length" | "sqrt" | "exp"
math-arg ::= "p.x" | "p.y" | scalar-expression
variable ::= "p.x" | "p.y" | "i" | "time"
float-literal ::= [0-9]+ "." [0-9]+
"""


class Predictor(BasePredictor):
    def setup(self):
        model = "codellama-7b-instruct.Q5_K_S.gguf"
        model_path = f"/models/{model}"
        model_url = f"https://weights.replicate.delivery/default/llamacpp/{model}"
        start = time.time()
        if not os.path.exists(model_path):
            print("Downloading model weights....")
            subprocess.check_call(["pget", model_url, model_path])
            print("Downloading weights took: ", time.time() - start)
        self.llm = Llama(
            model_path, n_ctx=4096, n_gpu_layers=-1, main_gpu=0, n_threads=1
        )

    def predict(
        self,
    ) -> ConcatenateIterator[str]:
        for tok in self.llm(
            PROMPT,
            grammar=LlamaGrammar.from_string(GRAMMAR),
            max_tokens=500,
            temperature=0.8,
            top_p=0.95,
            top_k=10,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            repeat_penalty=1.1,
            mirostat_mode=0,
            stream=True,
        ):
            yield tok["choices"][0]["text"]
