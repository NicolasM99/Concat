from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

# Shared bits of broken video: a channel split, a picture torn in rows,
# scan lines, static.
TV = """
fn split(uv: vec2<f32>, o: vec2<f32>) -> vec4<f32> {
    let g = sample(uv);
    return vec4<f32>(sample(uv + o).r, g.g, sample(uv - o).b, g.a);
}

fn scanlines(uv: vec2<f32>, amount: f32) -> f32 {
    return 1.0 - amount * step(0.5, fract(uv.y * frame.size.y / 3.0));
}

fn static_at(uv: vec2<f32>, t: f32) -> f32 {
    return hash(floor(uv * frame.size / 2.0), fract(t * 0.137) * 1000.0);
}
"""

def g(slug, name, order, desc, body, params, category="Glitch", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + NOISE + TV + body, params,
             shelves=kw.pop("shelves", ["Distortion & Glitch"]), **kw)

H = p("chroma_x", "Horizontal split", 0, 100, 60)
V = p("chroma_y", "Vertical split", 0, 100, 60)

PACKAGES = [
g("glitch", "Glitch", 10, "Rows of the picture tear sideways and its colours split in bursts.", """
struct Params { speed: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (6.0 + rate() * 10.0));
    let burst = step(0.55, hash(vec2<f32>(floor(t / 3.0), 0.0), 1.0));
    let row = floor(uv.y * 40.0);
    let tear = (hash(vec2<f32>(row, t), 2.0) - 0.5) * 0.08 * burst * params.range / 100.0;
    let q = vec2<f32>(fract(uv.x + select(0.0, tear, hash(vec2<f32>(row, t), 3.0) < 0.3)), uv.y);
    return split(q, vec2<f32>(0.006 + 0.01 * burst, 0.0) * params.range / 100.0);
}
""", [SPEED, p("range", "Range", 0, 100, 100)], intensity="range"),

g("level-glitch", "Level Glitch", 11, "Whole bands of the picture slip sideways in steps.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (4.0 + rate() * 8.0));
    let band = floor(uv.y * 8.0 + hash(vec2<f32>(t, 0.0), 4.0) * 3.0);
    let shift = (hash(vec2<f32>(band, t), 5.0) - 0.5) * 0.1 * step(0.6, hash(vec2<f32>(band, t), 6.0));
    return sample(vec2<f32>(fract(uv.x + shift), uv.y));
}
""", [SPEED]),

g("level-glitch-2", "Level Glitch 2", 12, "Bands of the picture slip and split their colours.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (4.0 + rate() * 8.0));
    let band = floor(uv.y * 14.0);
    let on = step(0.7, hash(vec2<f32>(band, t), 6.0));
    let shift = (hash(vec2<f32>(band, t), 5.0) - 0.5) * 0.15 * on;
    return split(vec2<f32>(fract(uv.x + shift), uv.y), vec2<f32>(0.01 * on, 0.0));
}
""", [SPEED]),

g("color-glitch-fx", "Color Glitch", 13, "Blocks of the picture flash into the wrong colours.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (4.0 + rate() * 8.0));
    let block = floor(uv * vec2<f32>(8.0, 12.0));
    let c = split(uv, vec2<f32>(0.004, 0.0));
    let on = hash(block, t) < 0.12;
    let turned = hue_rotate(c.rgb, 90.0 + 180.0 * hash(block, t + 1.0));
    return vec4<f32>(select(c.rgb, turned * 1.2, on), c.a);
}
""", [SPEED]),

g("color-glitch-2", "Color Glitch 2", 14, "The colours split apart and jitter in bursts.", """
struct Params { speed: f32, chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (6.0 + rate() * 10.0));
    let k = 0.5 + hash(vec2<f32>(t, 0.0), 7.0);
    let o = vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.015 * k;
    return split(uv, o);
}
""", [SPEED, p("chroma_x", "Horizontal split", 0, 100, 75), p("chroma_y", "Vertical split", 0, 100, 50)]),

g("x-signal", "X-Signal", 15, "A failing broadcast: rolling bars, colour bleed and snow.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let roll = fract(uv.y - t * 0.3);
    let bar = smoothstep(0.1, 0.0, abs(roll - 0.5)) * 0.5;
    let wobble = sin(uv.y * 80.0 + t * 20.0) * 0.003 * (1.0 + bar * 4.0);
    let c = split(uv + vec2<f32>(wobble, 0.0), vec2<f32>(0.006, 0.0));
    let n = static_at(uv, frame.time);
    let rgb = mix(c.rgb * (1.0 - bar * 0.5), vec3<f32>(n), 0.12 + bar * 0.3);
    return vec4<f32>(rgb * scanlines(uv, 0.15), c.a);
}
""", [SPEED]),

g("bad-tv", "Bad TV", 16, "A badly tuned television: wobbling picture, colour fringes, snow and scan lines.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0;
    let t = frame.time;
    let wobble = (vnoise(vec2<f32>(uv.y * 20.0, t * 5.0)) - 0.5) * 0.02 * k;
    let c = split(uv + vec2<f32>(wobble, 0.0), vec2<f32>(0.005 * k, 0.0));
    let n = static_at(uv, t);
    let rgb = mix(c.rgb, vec3<f32>(n), 0.2 * k);
    return vec4<f32>(rgb * scanlines(uv, 0.2 * k), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], intensity="strength"),

g("snow-glitch", "Snow Glitch", 17, "Bursts of video snow break up the picture.", """
struct Params { range: f32, noise: f32, chroma_x: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * 12.0);
    let band = step(1.0 - params.range / 100.0, hash(vec2<f32>(floor(uv.y * 20.0), t), 1.0));
    let c = split(uv, vec2<f32>(params.chroma_x / 100.0 * 0.01, 0.0));
    let n = static_at(uv, frame.time);
    let rgb = mix(c.rgb, vec3<f32>(n), clamp(band + params.noise / 100.0 * 0.2, 0.0, 1.0));
    return vec4<f32>(rgb, c.a);
}
""", [p("range", "Range", 0, 100, 15), p("noise", "Noise", 0, 100, 50), p("chroma_x", "Split", 0, 100, 55)]),

g("edgy", "Edgy", 18, "Hard, jagged colour edges flicker around everything in the picture.", """
struct Params { speed: f32, chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (6.0 + rate() * 10.0));
    let o = vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.012 * (0.4 + hash(vec2<f32>(t, 0.0), 1.0));
    let c = split(uv, o);
    let e = edge_at(uv);
    return vec4<f32>(c.rgb + vec3<f32>(e * 0.5, 0.0, e * 0.6), c.a);
}
""", [SPEED, p("chroma_x", "Horizontal split", 0, 100, 75), p("chroma_y", "Vertical split", 0, 100, 50)]),

g("tv-on", "TV On", 19, "An old TV switching on: a bright line opens out into the picture.", """
struct Params { speed: f32, strength: f32, chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = opening();
    let h = smoothstep(0.0, 0.6, t);
    let w = smoothstep(0.0, 0.25, t);
    let d = abs(uv - vec2<f32>(0.5)) * 2.0;
    if (d.y > max(h, 0.004) || d.x > w) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let q = vec2<f32>(0.5) + (uv - vec2<f32>(0.5)) / vec2<f32>(max(w, 0.01), max(h, 0.01));
    let o = vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.01 * (1.0 - t);
    let c = split(q, o);
    let flare = (1.0 - h) * params.strength / 100.0 * 4.0;
    return vec4<f32>(c.rgb + vec3<f32>(flare), c.a);
}
""", [SPEED, p("strength", "Flare", 0, 100, 50), H, V], category="Retro", card={"moment": 0.5}),

g("tv-off", "TV Off", 20, "An old TV switching off: the picture collapses to a line, then a dot.", """
struct Params { speed: f32, chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = closing();
    let h = 1.0 - smoothstep(0.0, 0.6, t);
    let w = 1.0 - smoothstep(0.6, 1.0, t);
    let d = abs(uv - vec2<f32>(0.5)) * 2.0;
    if (t >= 1.0 || d.y > max(h, 0.004) || d.x > max(w, 0.0)) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let q = vec2<f32>(0.5) + (uv - vec2<f32>(0.5)) / vec2<f32>(max(w, 0.01), max(h, 0.01));
    let o = vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.01 * t;
    let c = split(q, o);
    return vec4<f32>(c.rgb + vec3<f32>(t * 3.0), c.a);
}
""", [SPEED, H, V], category="Retro"),

g("old-tv-2", "Old TV 2", 21, "A curved old TV screen: rolling lines, a dull glow and faded colour.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = uv - vec2<f32>(0.5);
    let q = vec2<f32>(0.5) + d * (1.0 + 0.15 * dot(d, d));
    if (q.x < 0.0 || q.x > 1.0 || q.y < 0.0 || q.y > 1.0) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let c = split(q, vec2<f32>(0.002, 0.0));
    let roll = smoothstep(0.08, 0.0, abs(fract(q.y - frame.time * rate() * 0.2) - 0.5)) * 0.15;
    let faded = mix(c.rgb, vec3<f32>(luma(c.rgb)), 0.4) * (1.0 + roll);
    let vig = 1.0 - dot(d, d) * 1.2;
    return vec4<f32>(faded * scanlines(q, 0.25) * vig, c.a);
}
""", [SPEED], category="Retro"),

g("tv-colored-lines", "TV Colored Lines", 22, "Coloured bars of interference sweep down the picture.", """
struct Params { speed: f32, texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let band = fract(uv.y * 3.0 - frame.time * rate() * 0.5);
    let tint = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(band) + vec3<f32>(0.0, 0.33, 0.67)));
    let k = params.texture / 100.0;
    let rgb = mix(c.rgb, c.rgb * tint * tint * 1.8, 0.5 * k) * scanlines(uv, 0.2 * k);
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("texture", "Strength", 0, 100, 100)], category="Retro", intensity="texture"),

g("tv-lines", "TV Lines", 23, "Heavy television scan lines with a slight wave.", """
struct Params { texture: f32, distortion: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let wave = sin(uv.y * 200.0 + frame.time * 10.0) * 0.002 * params.distortion / 100.0;
    let c = sample(uv + vec2<f32>(wave, 0.0));
    return vec4<f32>(c.rgb * scanlines(uv, 0.45 * params.texture / 100.0), c.a);
}
""", [p("texture", "Lines", 0, 100, 100), p("distortion", "Wave", 0, 100, 100)], category="Retro", intensity="texture"),

g("noise-fx", "Noise", 24, "Coloured video noise over the picture.", """
struct Params { noise: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time;
    let n = vec3<f32>(static_at(uv, t), static_at(uv, t + 0.3), static_at(uv, t + 0.6)) - vec3<f32>(0.5);
    return vec4<f32>(c.rgb + n * params.noise / 100.0 * 0.4, c.a);
}
""", [p("noise", "Noise", 0, 100, 50)], category="Retro", intensity="noise"),

g("noise-1", "Noise 1", 25, "Grey static drifts over the picture.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = static_at(uv, floor(frame.time * (8.0 + rate() * 10.0)));
    return vec4<f32>(mix(c.rgb, vec3<f32>(n), 0.25), c.a);
}
""", [SPEED], category="Retro"),

g("noise-2", "Noise 2", 26, "Bands of static roll over the picture.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = static_at(uv, frame.time);
    let band = smoothstep(0.3, 0.0, abs(fract(uv.y * 2.0 - frame.time * rate()) - 0.5));
    return vec4<f32>(mix(c.rgb, vec3<f32>(n), 0.1 + band * 0.5), c.a);
}
""", [SPEED], category="Retro"),

g("black-noise", "Black Noise", 27, "Dark static crawls over a dimmed picture.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = static_at(uv, floor(frame.time * (8.0 + rate() * 10.0)));
    let dark = step(0.6, n);
    return vec4<f32>(c.rgb * (0.75 - dark * 0.6), c.a);
}
""", [SPEED], category="Retro"),

g("fuzzy", "Fuzzy", 28, "A fuzzy, smeared picture with colour fringes, like a bad tape.", """
struct Params { speed: f32, strength: f32, chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0;
    let wob = (vnoise(vec2<f32>(uv.y * 10.0, frame.time * rate() * 3.0)) - 0.5) * 0.01 * k;
    let o = vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.008;
    let c = split(uv + vec2<f32>(wob, 0.0), o);
    let soft = soften(uv, 3.0 * k);
    return vec4<f32>(mix(c.rgb, soft, 0.4 * k), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 100), p("chroma_x", "Horizontal split", 0, 100, 75), p("chroma_y", "Vertical split", 0, 100, 50)], category="Retro", intensity="strength"),

g("chromatic", "Chromatic", 29, "The colours of the picture pull apart and back on a beat.", """
struct Params { speed: f32, strength: f32, chroma_x: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = (0.5 + 0.5 * sin(frame.time * rate() * 6.2831853)) * params.strength / 100.0;
    return split(uv, vec2<f32>(params.chroma_x / 100.0 * 0.02 * k, 0.0));
}
""", [SPEED, p("strength", "Strength", 0, 100, 100), p("chroma_x", "Split", 0, 100, 60)], intensity="strength"),

g("chromatic-quirk", "Chromatic Quirk", 30, "A steady, quirky split of the picture's colours.", """
struct Params { chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    return split(uv, vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.012);
}
""", [p("chroma_x", "Horizontal split", 0, 100, 60), p("chroma_y", "Vertical split", 0, 100, 50)]),

g("shadow-ghost", "Shadow", 31, "A coloured shadow of the picture trails it, out of step.", """
struct Params { speed: f32, chroma_x: f32, chroma_y: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * rate() * 3.0;
    let o = vec2<f32>(params.chroma_x * sin(t), params.chroma_y * cos(t * 0.8)) / 100.0 * 0.03;
    let ghost = sample(uv + o);
    let tinted = ghost.rgb * vec3<f32>(0.4, 0.6, 1.4);
    return vec4<f32>(mix(c.rgb, max(c.rgb, tinted), 0.6 * params.range / 100.0), c.a);
}
""", [SPEED, p("chroma_x", "Horizontal", 0, 100, 75), p("chroma_y", "Vertical", 0, 100, 75), p("range", "Strength", 0, 100, 100)], intensity="range"),

g("film-2", "Film 2", 32, "A film print with misregistered colours and gentle grain.", """
struct Params { chroma_x: f32, chroma_y: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = split(uv, vec2<f32>(params.chroma_x, params.chroma_y) / 100.0 * 0.006);
    let rgb = film_curve(c.rgb, 0.3, 0.3) + grain_at(uv, 0.04);
    return vec4<f32>(rgb, c.a);
}
""", [p("chroma_x", "Horizontal split", 0, 100, 55), p("chroma_y", "Vertical split", 0, 100, 55)], category="Retro"),

g("spectrum-scan", "Spectrum Scan", 33, "A band of rainbow light scans up and down the picture.", RAINBOW + """
struct Params { speed: f32, strength: f32, luminance: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let pos = 0.5 + 0.5 * sin(frame.time * rate() * 2.0);
    let w = mix(0.03, 0.3, params.range / 100.0);
    let band = exp(-pow((uv.y - pos) / w, 2.0));
    let tint = rainbow(fract((uv.y - pos) / w * 0.3 + 0.5));
    let rgb = mix(c.rgb, c.rgb * tint * 2.0, band * params.strength / 100.0) + tint * band * params.luminance / 100.0 * 0.4;
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 61), p("luminance", "Glow", 0, 100, 64), p("range", "Width", 0, 100, 33)], category="Light", intensity="strength"),

g("blu-ray-scanning", "Blu-ray Scanning", 34, "A blue laser line scans the picture, leaving a soft glow.", """
struct Params { speed: f32, luminance: f32, blur: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let pos = fract(frame.time * rate() * 0.5);
    let w = mix(0.01, 0.15, params.range / 100.0);
    let d = uv.y - pos;
    let line = exp(-d * d / (w * w * 0.05));
    let trail = select(0.0, exp(d / w), d < 0.0);
    let soft = soften(uv, 1.0 + params.blur / 100.0 * 6.0);
    let c = sample(uv);
    let rgb = mix(c.rgb, soft, trail * 0.6) + vec3<f32>(0.2, 0.5, 1.5) * (line + trail * 0.3) * params.luminance / 100.0;
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("luminance", "Glow", 0, 100, 50), p("blur", "Blur", 0, 100, 30), p("range", "Width", 0, 100, 70)], category="Light", intensity="luminance"),

g("color-phosphor", "Color Phosphor", 35, "The picture drawn in the coloured dots of a CRT's phosphors.", """
struct Params { size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let px = uv * frame.size / max(params.size / 100.0 * 6.0 + 2.0, 1.0);
    let column = i32(floor(px.x)) % 3;
    var mask = vec3<f32>(0.35);
    if (column == 0) { mask.r = 1.4; } else if (column == 1) { mask.g = 1.4; } else { mask.b = 1.4; }
    let row = 0.8 + 0.2 * step(0.3, fract(px.y));
    return vec4<f32>(c.rgb * mask * row * 1.2, c.a);
}
""", [p("size", "Size", 0, 100, 30)], category="Retro"),

g("vx1000", "VX1000", 36, "The skate-video look of a VX1000 with a fisheye: bent edges, fringes and crunchy contrast.", """
struct Params { distortion: f32, chroma_x: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(aspect, 1.0);
    let k = params.distortion / 100.0 * 0.6;
    let q = d / (1.0 + k * dot(d, d)) * (1.0 + k * 0.3) / vec2<f32>(aspect, 1.0) + vec2<f32>(0.5);
    let c = split(q, vec2<f32>(params.chroma_x / 100.0 * 0.006, 0.0) * length(d) * 2.0);
    let rgb = s_curve(saturation(c.rgb, 1.15), 0.4);
    let vig = 1.0 - smoothstep(0.5, 0.9, length(d)) * 0.7;
    return vec4<f32>(rgb * vig, c.a);
}
""", [p("distortion", "Distortion", 0, 100, 90), p("chroma_x", "Split", 0, 100, 60)], category="Retro", intensity="distortion"),

g("bw-vhs", "B&W VHS", 37, "Black-and-white VHS tape: smeared, noisy, with tracking wobble.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0;
    let wob = (vnoise(vec2<f32>(uv.y * 30.0, frame.time * rate() * 4.0)) - 0.5) * 0.01 * k;
    let c = sample(uv + vec2<f32>(wob, 0.0));
    let soft = soften(uv, 2.0);
    let l = luma(mix(c.rgb, soft, 0.4));
    let n = (static_at(uv, frame.time) - 0.5) * 0.15 * k;
    let track = smoothstep(0.02, 0.0, abs(fract(uv.y - frame.time * 0.1) - 0.95)) * 0.4 * k;
    return vec4<f32>(vec3<f32>(l + n + track) * scanlines(uv, 0.12), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 50)], category="Retro", intensity="strength"),

g("camcorder", "Camcorder", 38, "A home camcorder: REC light, time code bars and a soft video look.", """
struct Params { look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = split(uv, vec2<f32>(0.002, 0.0));
    var rgb = mix(c.rgb, soften(uv, 2.0), 0.3) * scanlines(uv, 0.1 * params.look / 100.0);
    rgb = saturation(rgb, 1.15);
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let m = 0.06;
    let len = 0.08;
    let t = 0.005;
    let cx = min(px.x - m, w - m - px.x);
    let cy = min(px.y - m, 1.0 - m - px.y);
    let bracket = (abs(cx) < t && cy >= -t && cy < len) || (abs(cy) < t && cx >= -t && cx < len);
    let dot = length(px - vec2<f32>(m + 0.045, m + 0.045)) < 0.016 && fract(frame.time) < 0.6;
    rgb = select(rgb, vec3<f32>(1.0), bracket);
    rgb = select(rgb, vec3<f32>(1.0, 0.05, 0.05), dot);
    // A battery block at the top right.
    let b = px - vec2<f32>(w - m - 0.1, m + 0.03);
    let battery = abs(b.x) < 0.035 && abs(b.y) < 0.015 && (abs(b.x) > 0.03 || abs(b.y) > 0.01 || b.x < 0.01);
    rgb = select(rgb, vec3<f32>(1.0), battery);
    return vec4<f32>(rgb, c.a);
}
""", [p("look", "Lines", 0, 100, 60)], category="Retro"),

g("camcorder-2", "Camcorder 2", 39, "A camcorder viewfinder with a centre cross and a grainy, warm image.", """
struct Params { look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    var rgb = c.rgb * vec3<f32>(1.08, 1.0, 0.9) + grain_at(uv, 0.06 * params.look / 100.0);
    let px = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let cross = (abs(px.x) < 0.003 && abs(px.y) < 0.04) || (abs(px.y) < 0.003 && abs(px.x) < 0.04);
    let frame_line = abs(abs(px.y) - 0.42) < 0.003 && abs(px.x) < frame.size.x / frame.size.y * 0.46;
    rgb = select(rgb, vec3<f32>(1.0), cross || frame_line);
    return vec4<f32>(rgb, c.a);
}
""", [p("look", "Grain", 0, 100, 60)], category="Retro"),

g("camcorder-3", "Camcorder 3", 40, "A worn camcorder tape: wobble, bleed and a date stamp's warm cast.", """
struct Params { look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.look / 100.0;
    let wob = (vnoise(vec2<f32>(uv.y * 20.0, frame.time * 3.0)) - 0.5) * 0.006 * k;
    let c = split(uv + vec2<f32>(wob, 0.0), vec2<f32>(0.004 * k, 0.0));
    let rgb = fade(c.rgb * vec3<f32>(1.1, 0.98, 0.85), 0.05 * k) * scanlines(uv, 0.08 * k);
    return vec4<f32>(rgb, c.a);
}
""", [p("look", "Wear", 0, 100, 60)], category="Retro"),

g("retro-cam", "Retro Cam", 41, "An old digital camera: crushed contrast, cool cast and a little noise.", """
struct Params { look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.look / 100.0;
    let c = sample(uv);
    let rgb = s_curve(c.rgb * mix(vec3<f32>(1.0), vec3<f32>(0.95, 1.0, 1.1), k), 0.5 * k) + grain_at(uv, 0.05 * k);
    let vig = 1.0 - smoothstep(0.4, 0.95, length(uv - vec2<f32>(0.5)) * 1.3) * 0.5 * k;
    return vec4<f32>(rgb * vig, c.a);
}
""", [p("look", "Strength", 0, 100, 70)], category="Retro"),

g("spooky-camera", "Spooky Camera", 42, "Night-vision found footage: green, grainy, flickering.", """
struct Params { look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.look / 100.0;
    let c = sample(uv);
    let l = luma(c.rgb) * (1.0 + (hash(vec2<f32>(floor(frame.time * 12.0), 0.0), 1.0) - 0.5) * 0.3);
    let green = vec3<f32>(l * 0.4, l * 1.3, l * 0.45) + grain_at(uv, 0.12);
    let vig = 1.0 - smoothstep(0.3, 0.8, length(uv - vec2<f32>(0.5))) * 0.8;
    return vec4<f32>(mix(c.rgb, green * vig * scanlines(uv, 0.15), k), c.a);
}
""", [p("look", "Strength", 0, 100, 80)], category="Retro", intensity="look"),

g("invisible-person", "Invisible Person", 43, "A shimmering, refracting cloak bends the picture as if something invisible moved through it.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let q = uv * 4.0 + vec2<f32>(t * 0.4, t * 0.25);
    let n = vec2<f32>(fbm(q), fbm(q + vec2<f32>(3.1, 7.7))) - vec2<f32>(0.5);
    let k = params.strength / 100.0;
    let c = split(uv + n * 0.04 * k, n * 0.01 * k);
    return vec4<f32>(c.rgb + vec3<f32>(edge_at(uv + n * 0.04 * k) * 0.2 * k), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 50)], intensity="strength"),

g("unreal", "Unreal", 44, "The picture echoes in shifted, hue-turned copies, like a broken hologram.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let c = sample(uv);
    let a = sample(uv + vec2<f32>(sin(t) * 0.02, 0.0));
    let b = sample(uv - vec2<f32>(0.0, cos(t * 1.3) * 0.02));
    let rgb = c.rgb * 0.6 + hue_rotate(a.rgb, 120.0) * 0.25 + hue_rotate(b.rgb, 240.0) * 0.25;
    return vec4<f32>(rgb, c.a);
}
""", [p("speed", "Speed", 0, 100, 100)]),

g("seventies", "70's", 45, "A 1970s broadcast: warm, faded, bleeding colour with soft scan lines.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let wob = sin(uv.y * 50.0 + frame.time * rate() * 10.0) * 0.0015;
    let c = split(uv + vec2<f32>(wob, 0.0), vec2<f32>(0.004, 0.0));
    let rgb = fade(c.rgb * vec3<f32>(1.12, 1.0, 0.8), 0.06) * scanlines(uv, 0.1);
    return vec4<f32>(saturation(rgb, 0.85), c.a);
}
""", [SPEED], category="Retro"),

]
