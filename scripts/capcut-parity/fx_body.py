from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

# CapCut's character effects find the person in the shot. A Concat effect
# sees the picture alone, so these draw around the outlines in the picture
# (its edges) or around a point placed on the person, and say so.
NOTE = " Drawn around the edges in the picture; place it on a clip with a clear subject."
POINT_NOTE = " Drawn about the point you place on the subject."

CENTRE = {"key": "centre", "label": "Subject", "type": "point", "default": 0.5}

BODY = """
/// Distance from `uv` to `at`, in frame heights.
fn reach(uv: vec2<f32>, at: vec2<f32>) -> f32 {
    return length((uv - at) * vec2<f32>(frame.size.x / frame.size.y, 1.0));
}

/// How much `uv` is an outline in the picture, softened a little so a
/// glow can be built on it.
fn outline(uv: vec2<f32>, spread: f32) -> f32 {
    let t = texel() * spread;
    var e = edge_at(uv);
    e = max(e, edge_at(uv + vec2<f32>(t.x, 0.0)) * 0.7);
    e = max(e, edge_at(uv - vec2<f32>(t.x, 0.0)) * 0.7);
    e = max(e, edge_at(uv + vec2<f32>(0.0, t.y)) * 0.7);
    e = max(e, edge_at(uv - vec2<f32>(0.0, t.y)) * 0.7);
    return smoothstep(0.08, 0.5, e);
}
"""

def b(slug, name, order, desc, body, params, category="Body", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    # The outline helpers draw in the display space; a shader that does
    # not read them keeps the working space.
    body_lib = BODY if "outline(" in body or "edge_at(" in body else BODY.split("/// How much")[0]
    return E(slug, name, category, order, desc, clock + MOVE + NOISE + RAINBOW + HEART + GLINT + HUE + body_lib + body, params, **kw)

def aura(tint, flame=False, spread=4.0, darken=0.0):
    flicker = "fbm(uv * 8.0 + vec2<f32>(0.0, -frame.time * 2.0))" if flame else "1.0"
    return """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let wobble = (vec2<f32>(fbm(uv * 6.0 + vec2<f32>(frame.time)), fbm(uv * 6.0 - vec2<f32>(frame.time))) - vec2<f32>(0.5)) * 0.01;
    let e = outline(uv + wobble, SPREAD) * FLICKER;
    let tint = TINT;
    return vec4<f32>(c.rgb * (1.0 - DARKEN * k) + tint * e * 2.0 * k, c.a);
}
""".replace("SPREAD", f"{spread}").replace("FLICKER", flicker).replace("TINT", tint).replace("DARKEN", f"{darken}")

def trail(tint, copies, step, fade, mode="dir"):
    offset = {
        "dir": "vec2<f32>(-0.012, 0.0) * fi * STEP * (0.6 + 0.4 * sin(frame.time * 2.0))",
        "orbit": "vec2<f32>(cos(frame.time * 2.0 + fi), sin(frame.time * 2.0 + fi)) * 0.01 * fi * STEP",
        "down": "vec2<f32>(0.0, -0.012) * fi * STEP",
        "scatter": "(vec2<f32>(hash(vec2<f32>(fi, floor(frame.time * 6.0)), 1.0), hash(vec2<f32>(fi, floor(frame.time * 6.0)), 2.0)) - vec2<f32>(0.5)) * 0.06 * STEP",
    }[mode].replace("STEP", f"{step}")
    return """
struct Params { strength: f32 }

// Copies of the picture trailing behind it, each fainter and tinted.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    var rgb = c.rgb;
    for (var i = 1; i <= COPIES; i++) {
        let fi = f32(i);
        let o = OFFSET;
        let g = sample(uv + o * k);
        let w = pow(FADE, fi) * k;
        let tint = TINT;
        rgb = max(rgb, mix(rgb, g.rgb * tint, w));
    }
    return vec4<f32>(rgb, c.a);
}
""".replace("COPIES", str(copies)).replace("OFFSET", offset).replace("FADE", f"{fade}").replace("TINT", tint)

S = [p("strength", "Strength", 0, 100, 80)]

PACKAGES = [
b("aura", "Aura", 10, "A soft coloured aura glows around the outlines." + NOTE, aura("rainbow(fract(frame.time * 0.1 + uv.y * 0.3))", spread=6.0), S, intensity="strength"),
b("thermal-aura", "Thermal Aura", 11, "A heat-camera aura: outlines glow from blue through to red over a darkened, false-colour picture." + NOTE, """
struct Params { strength: f32 }

fn heat(x: f32) -> vec3<f32> {
    return clamp(vec3<f32>(x * 3.0 - 1.5, sin(x * 3.14159265), 1.5 - x * 3.0), vec3<f32>(0.0), vec3<f32>(1.0));
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let l = clamp(luma(c.rgb), 0.0, 1.0);
    let e = outline(uv, 5.0);
    let thermal = heat(clamp(l + e * 0.4, 0.0, 1.0));
    return vec4<f32>(mix(c.rgb, thermal + heat(1.0) * e, k), c.a);
}
""", S, intensity="strength"),
b("thermal-aura-2", "Thermal Aura 2", 12, "A glowing infrared halo traces the outlines while the rest cools to blue." + NOTE, aura("mix(vec3<f32>(1.0, 0.2, 0.05), vec3<f32>(1.0, 0.9, 0.2), e)", spread=6.0, darken=0.5), S, intensity="strength"),
b("flame-outline", "Flame Outline", 13, "Flames flicker along the outlines." + NOTE, aura("vec3<f32>(1.6, 0.55, 0.08)", flame=True, spread=5.0, darken=0.2), S, intensity="strength"),
b("neon-doodle", "Neon Doodle", 14, "Shaky neon doodle lines trace the outlines, jumping frame to frame." + NOTE, """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = floor(frame.time * 8.0);
    let j = (vec2<f32>(hash(vec2<f32>(t, 1.0), 1.0), hash(vec2<f32>(t, 2.0), 1.0)) - vec2<f32>(0.5)) * 0.008;
    let e = smoothstep(0.3, 0.6, outline(uv + j, 2.0));
    let tint = rainbow(fract(t * 0.13));
    let k = params.strength / 100.0;
    return vec4<f32>(c.rgb * (1.0 - 0.2 * k) + tint * e * 2.5 * k, c.a);
}
""", S, intensity="strength"),
b("neon-variation", "Neon Variation", 15, "Neon outlines that cycle through colours on a dark picture." + NOTE, aura("rainbow(fract(frame.time * 0.5))", spread=3.0, darken=0.6), S, intensity="strength"),
b("fluoro-flash", "Fluoro Flash", 16, "Outlines flash fluorescent on the beat." + NOTE, """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let beat = exp(-fract(frame.time * 2.0) * 5.0);
    let e = outline(uv, 4.0);
    let tint = select(vec3<f32>(0.3, 1.6, 0.2), vec3<f32>(1.6, 0.2, 1.2), fract(floor(frame.time * 2.0) * 0.5) < 0.25);
    return vec4<f32>(c.rgb + tint * e * beat * 2.0 * params.strength / 100.0, c.a);
}
""", S, intensity="strength"),
b("streamer-stroke", "Streamer Stroke", 17, "A glowing streamer races along the outlines." + NOTE, """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let e = outline(uv, 3.0);
    let run = pow(0.5 + 0.5 * sin((uv.x + uv.y) * 20.0 - frame.time * 6.0), 8.0);
    let tint = rainbow(fract(uv.x + frame.time * 0.3));
    return vec4<f32>(c.rgb + tint * e * run * 3.0 * params.strength / 100.0, c.a);
}
""", S, intensity="strength"),
b("color-fringe", "Color Fringe", 18, "Bright colour fringes split off the outlines." + NOTE, """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0 * 0.012;
    let g = sample(uv);
    let r = sample(uv + vec2<f32>(k, 0.0));
    let bl = sample(uv - vec2<f32>(k, 0.0));
    let e = outline(uv, 2.0);
    return vec4<f32>(vec3<f32>(r.r, g.g, bl.b) + vec3<f32>(0.3, 0.0, 0.5) * e * params.strength / 100.0, g.a);
}
""", S, intensity="strength"),
b("chroma-diffusion", "Chroma Diffusion", 19, "The colours of the picture diffuse outward in red, green and blue ghosts.", trail("vec3<f32>(1.0, 0.4, 0.4)", 3, 1.2, 0.6, "orbit"), S, intensity="strength"),
b("dopelgangers", "Dopelgangers", 20, "Doubles of the picture step out to either side and back.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let o = vec2<f32>(0.12 * (0.5 + 0.5 * sin(frame.time * 1.5)) * k, 0.0);
    let left = sample(uv + o);
    let right = sample(uv - o);
    return vec4<f32>(max(c.rgb, (left.rgb + right.rgb) * 0.5 * 0.8), c.a);
}
""", S, intensity="strength"),
b("phantom", "Phantom", 21, "A pale phantom of the picture drifts off it and fades.", trail("vec3<f32>(0.7, 0.85, 1.2)", 4, 1.5, 0.55, "dir"), S, intensity="strength"),
b("ghost", "Ghost", 22, "A translucent, blue-white ghost of the picture floats up out of it.", trail("vec3<f32>(0.75, 0.9, 1.3)", 3, 2.0, 0.6, "down"), S, intensity="strength"),
b("star-trails", "Star Trails", 23, "Glittering trails stream behind the picture's bright parts.", trail("vec3<f32>(1.0, 0.95, 0.7) * (1.0 + glint(fract(uv * 30.0) - vec2<f32>(0.5), 0.5))", 5, 1.0, 0.7, "dir"), S, intensity="strength"),
b("shape-trails", "Shape Trails", 24, "Coloured copies of the picture trail behind it.", trail("rainbow(fi * 0.2 + frame.time * 0.2)", 4, 1.2, 0.65, "dir"), S, intensity="strength"),
b("shape-trails-2", "Shape Trails 2", 25, "Coloured copies of the picture orbit around it.", trail("rainbow(fi * 0.25 + frame.time * 0.3)", 4, 1.0, 0.65, "orbit"), S, intensity="strength"),
b("light-trails", "Light Trails", 26, "Streaks of light trail behind the bright parts of the picture.", trail("vec3<f32>(1.5, 1.3, 1.0)", 6, 0.8, 0.75, "dir"), S, intensity="strength"),
b("flame-trails", "Flame Trails", 27, "Fiery copies of the picture trail behind it.", trail("mix(vec3<f32>(1.8, 0.8, 0.1), vec3<f32>(1.2, 0.2, 0.02), fi / 5.0)", 5, 1.0, 0.7, "down"), S, intensity="strength"),
b("speed-streaks", "Speed Streaks", 28, "The picture streaks sideways as if moving at speed, speed lines across it.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0;
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 8; i++) {
        sum += sample(uv + vec2<f32>(f32(i) * 0.006 * k, 0.0));
    }
    let c = sum / 8.0;
    let line = step(0.92, hash(vec2<f32>(floor(uv.y * 80.0), floor(frame.time * 10.0)), 1.0)) * smoothstep(0.0, 0.5, fract(uv.x - frame.time * 3.0));
    return vec4<f32>(c.rgb + vec3<f32>(line * 0.6 * k), c.a);
}
""", S, intensity="strength"),
b("frame-scatter", "Frame Scatter", 29, "Copies of the picture scatter and jump around it.", trail("vec3<f32>(1.0)", 3, 1.0, 0.6, "scatter"), S, intensity="strength"),
b("frame-scatter-2", "Frame Scatter 2", 30, "Tinted copies of the picture scatter and jump around it.", trail("rainbow(fi * 0.33)", 3, 1.4, 0.6, "scatter"), S, intensity="strength"),
b("apparate", "Apparate 1", 31, "The picture shimmers into being out of a twist of light at the start of the clip.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = opening();
    let k = 1.0 - t;
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let a = k * 3.0 * (1.0 - smoothstep(0.0, 0.6, length(d)));
    let q = vec2<f32>(d.x * cos(a) - d.y * sin(a), d.x * sin(a) + d.y * cos(a)) * frame.size.y / frame.size + vec2<f32>(0.5);
    let c = sample(q);
    return vec4<f32>(c.rgb * t + vec3<f32>(0.8, 0.9, 1.0) * k * k * 1.5, c.a);
}
""", [SPEED], card={"moment": 0.4}),
b("sinking", "Sinking", 32, "The picture sinks and ripples as if dropping into water.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let sink = fract(t * 0.3) * 0.3;
    let wave = sin(uv.x * 30.0 + t * 4.0) * 0.006 * smoothstep(0.5 - sink, 1.0, uv.y);
    let c = sample(vec2<f32>(uv.x, uv.y - sink + wave));
    let water = smoothstep(1.0 - sink - 0.02, 1.0 - sink + 0.02, uv.y);
    return vec4<f32>(mix(c.rgb, c.rgb * vec3<f32>(0.5, 0.75, 1.0), water), c.a);
}
""", [SPEED]),
b("consciousness", "Consciousness", 33, "A dreamlike out-of-body double of the picture rises and fades.", trail("vec3<f32>(1.0, 0.9, 1.2)", 2, 3.0, 0.5, "down"), S, intensity="strength"),
b("cutout-poster", "Cutout Poster", 34, "The picture as a bold, flat-coloured poster with thick outlines.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let levels = 4.0;
    let poster = floor(clamp(c.rgb, vec3<f32>(0.0), vec3<f32>(1.0)) * levels + 0.5) / levels;
    let e = smoothstep(0.2, 0.4, edge_at(uv));
    let rgb = mix(saturation(poster, 1.4), vec3<f32>(0.02), e);
    return vec4<f32>(mix(c.rgb, rgb, params.strength / 100.0) + max(c.rgb - vec3<f32>(1.0), vec3<f32>(0.0)), c.a);
}
""", S, intensity="strength"),
b("dot-shadow", "Dot Shadow", 35, "A halftone-dot shadow of the picture falls behind it.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let s = sample(uv - vec2<f32>(0.02, -0.02));
    let cell = 6.0;
    let local = fract(uv * frame.size / cell) - vec2<f32>(0.5);
    let l = clamp(luma(s.rgb), 0.0, 1.0);
    let dot = smoothstep(0.45 * l, 0.45 * l - 0.1, length(local));
    let shade = mix(c.rgb, vec3<f32>(0.9, 0.2, 0.5), dot * 0.6 * params.strength / 100.0);
    return vec4<f32>(shade, c.a);
}
""", S, intensity="strength"),
]
