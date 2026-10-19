from lib_wgsl import *

# Effects with a Progress knob that reveal the clip: an animation rides
# them over its window, and with keys they are reveals of their own.
PROGRESS = {"key": "progress", "label": "Progress", "min": 0, "max": 100, "default": 50, "step": 1, "unit": "%", "animate": True}
DIRS = p("direction", "Direction", 0, 3, 0, values=[0, 1, 2, 3], labels=["Left to right", "Right to left", "Top to bottom", "Bottom to top"])

COORD = """
fn along(uv: vec2<f32>, direction: f32) -> f32 {
    if (direction < 0.5) {
        return uv.x;
    } else if (direction < 1.5) {
        return 1.0 - uv.x;
    } else if (direction < 2.5) {
        return uv.y;
    }
    return 1.0 - uv.y;
}
"""

def R(slug, name, order, desc, wgsl, params, category="Reveal"):
    return E(slug, name, category, order, desc, wgsl, params, intensity="progress", card={"params": {"progress": 60}})

PACKAGES = [
# CapCut's Zoom 2 In, from its package: the clip at 0.4 of its size grows
# back with a quartic ease, mirror images of it filling the frame round it,
# under a 26-tap dithered zoom blur toward its centre that is gone by 60 %.
R("zoom-2-blur", "Zoom 2 Blur", 40, "Shrinks the clip toward its centre, mirrored copies round it, under a zoom blur; the progress grows it back and clears the blur.", """
struct Params { progress: f32 }

fn mirrored(x: f32) -> f32 {
    return 1.0 - abs(abs(x) - 1.0);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let p = clamp(params.progress / 100.0, 0.0, 1.0);
    let s = 0.4 + 0.6 * (1.0 - pow(1.0 - p, 4.0));
    let blur = 0.4 * (max(1.0 - p, 0.4) - 0.4);
    let u = vec2<f32>(0.5) + (uv - vec2<f32>(0.5)) / s;
    if (u.x < -1.0 || u.x > 2.0 || u.y < -1.0 || u.y > 2.0) {
        return vec4<f32>(0.0);
    }
    let pixel = vec3<f32>(uv * frame.size + vec2<f32>(0.5), 0.5);
    let offset = fract(sin(dot(pixel, vec3<f32>(12.9898, 78.233, 151.7182))) * 43758.5453);
    var acc = vec4<f32>(0.0);
    var total = 0.0;
    for (var t = 0; t <= 25; t = t + 1) {
        let pc = (f32(t) + offset) / 25.0;
        let w = 4.0 * (pc - pc * pc);
        let c = u + (vec2<f32>(0.5) - u) * pc * blur;
        acc = acc + sample(vec2<f32>(mirrored(c.x), mirrored(c.y))) * w;
        total = total + w;
    }
    return acc / total;
}
""", [PROGRESS]),
R("reveal-wipe", "Reveal Wipe", 10, "Wipes the clip on from one side; the progress is how much of it shows.", COORD + """
struct Params { progress: f32, direction: f32, softness: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let soft = max(params.softness / 100.0, 0.001) * 0.2;
    let edge = params.progress / 100.0 * (1.0 + soft);
    let m = smoothstep(edge, edge - soft, along(uv, params.direction));
    return vec4<f32>(c.rgb, c.a * m);
}
""", [PROGRESS, DIRS, p("softness", "Softness", 0, 100, 20)]),
R("reveal-blinds", "Reveal Blinds", 11, "Shows the clip through blinds that open; the progress is how far.", COORD + """
struct Params { progress: f32, direction: f32, count: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let local = fract(along(uv, params.direction) * max(params.count, 1.0));
    let m = step(local, params.progress / 100.0);
    return vec4<f32>(c.rgb, c.a * m);
}
""", [PROGRESS, DIRS, p("count", "Blinds", 2, 24, 8, unit="")]),
R("reveal-iris", "Reveal Iris", 12, "Shows the clip through a circle that opens from the middle.", """
struct Params { progress: f32, softness: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = length((uv - vec2<f32>(0.5)) * frame.size) / (0.5 * length(frame.size));
    let soft = max(params.softness / 100.0, 0.001) * 0.2;
    let r = params.progress / 100.0 * (1.0 + soft);
    return vec4<f32>(c.rgb, c.a * smoothstep(r, r - soft, d));
}
""", [PROGRESS, p("softness", "Softness", 0, 100, 10)]),
R("reveal-clock", "Reveal Clock", 13, "Shows the clip as a clock hand sweeps round.", """
struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * frame.size;
    let a = fract(atan2(d.x, -d.y) / 6.2831853 + 1.0);
    return vec4<f32>(c.rgb, c.a * step(a, params.progress / 100.0));
}
""", [PROGRESS]),
R("reveal-tiles", "Reveal Tiles", 14, "Shows the clip tile by tile in a scattered order, like a puzzle filling in.", """
struct Params { progress: f32, tiles: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = max(params.tiles, 2.0);
    let cells = vec2<f32>(n, max(floor(n * frame.size.y / frame.size.x + 0.5), 1.0));
    let h = hash(floor(uv * cells), 3.0);
    return vec4<f32>(c.rgb, c.a * step(h, params.progress / 100.0 * 1.001));
}
""", [PROGRESS, p("tiles", "Tiles", 2, 24, 6, unit="")]),
R("reveal-split", "Reveal Split", 15, "Shows the clip as it opens out from a line through the middle.", """
struct Params { progress: f32, direction: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = select(abs(uv.y - 0.5), abs(uv.x - 0.5), params.direction < 0.5) * 2.0;
    return vec4<f32>(c.rgb, c.a * step(d, params.progress / 100.0));
}
""", [PROGRESS, p("direction", "Opening", 0, 1, 0, values=[0, 1], labels=["Side to side", "Up and down"])]),
R("reveal-words", "Reveal Words", 16, "On a title, shows its words one after another; the progress is how many.", """
struct Params { progress: f32, softness: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let order = reveal_order(uv);
    let soft = max(params.softness / 100.0, 0.001) * 0.3;
    let edge = params.progress / 100.0 * (1.0 + soft);
    let m = smoothstep(edge, edge - soft, order + 0.0001);
    return vec4<f32>(c.rgb, c.a * m);
}
""", [PROGRESS, p("softness", "Softness", 0, 100, 0)], category="Text"),
R("reveal-flame", "Reveal Flame", 17, "Burns the clip on from the bottom up behind a ragged edge of fire.", NOISE + """
struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = fbm(vec2<f32>(uv.x * 6.0, uv.y * 3.0 + frame.time * 2.0));
    let field = (1.0 - uv.y) * 0.8 + n * 0.2;
    let edge = params.progress / 100.0 * 1.25;
    let d = edge - field;
    let m = step(0.0, d);
    let glow = exp(-abs(d) / 0.03) * step(params.progress, 99.9);
    return vec4<f32>(c.rgb + vec3<f32>(2.0, 0.7, 0.1) * glow, max(c.a * m, glow * c.a));
}
""", [PROGRESS]),
R("rgb-scanlines", "RGB Scanlines", 18, "Splits the clip into red, green and blue with heavy scan lines; the amount is how strongly.", """
struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.progress / 100.0;
    let o = vec2<f32>(0.02 * k, 0.0);
    let g = sample(uv);
    let r = sample(uv + o);
    let b = sample(uv - o);
    let lines = 1.0 - 0.5 * k * step(0.5, fract(uv.y * frame.size.y / 4.0));
    return vec4<f32>(vec3<f32>(r.r, g.g, b.b) * lines, max(g.a, max(r.a, b.a)));
}
""", [PROGRESS]),
R("crt-bands", "CRT Bands", 19, "Rolls bright CRT bands and jitter over the clip; the amount is how strongly.", """
struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.progress / 100.0;
    let band = floor(uv.y * 12.0 - frame.time * 8.0);
    let shift = (hash(vec2<f32>(band, floor(frame.time * 20.0)), 1.0) - 0.5) * 0.08 * k;
    let c = sample(vec2<f32>(uv.x + shift, uv.y));
    let bright = 1.0 + k * 0.8 * step(0.7, hash(vec2<f32>(band, 2.0), 3.0));
    return vec4<f32>(c.rgb * bright, c.a);
}
""", [PROGRESS]),
R("gray-mask", "Gray Mask", 20, "Drains the clip to grey and darkens it; the amount is how far.", """
struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.progress / 100.0;
    return vec4<f32>(mix(c.rgb, vec3<f32>(luma(c.rgb) * 0.6), k), c.a);
}
""", [PROGRESS]),
R("anime-frame", "Anime Frame", 21, "Speed lines and a bright flash over the clip, like a frame from an anime; the amount is how strongly.", """
struct Params { progress: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.progress / 100.0;
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let a = atan2(d.y, d.x);
    let lines = step(0.8, hash(vec2<f32>(floor(a * 60.0), floor(frame.time * 15.0)), 1.0)) * smoothstep(0.2, 0.6, length(d));
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0), clamp(lines * k + k * k * 0.3, 0.0, 1.0)), c.a);
}
""", [PROGRESS]),
]
