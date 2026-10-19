from lib_wgsl import *

SPEED = p("speed", "Speed", 0, 100, 33)

# How fast a loop runs, in cycles a second, and how long a one-shot takes,
# in seconds, from a Speed knob.
CLOCK = """
fn rate() -> f32 {
    return 0.3 + params.speed / 100.0 * 3.0;
}

fn span() -> f32 {
    return mix(2.5, 0.25, params.speed / 100.0);
}

/// How far the clip is into its opening `span`, 0..1.
fn opening() -> f32 {
    return clamp(frame.clip_time / span(), 0.0, 1.0);
}

/// How far the clip is into its closing `span`, 0..1; 0 on a layer with no
/// end of its own.
fn closing() -> f32 {
    if (frame.clip_duration <= 0.0) {
        return 0.0;
    }
    return clamp((frame.clip_time - (frame.clip_duration - span())) / span(), 0.0, 1.0);
}
"""

# The picture moved, turned and grown about its centre, edges mirrored.
MOVE = MIRROR + """
fn moved(uv: vec2<f32>, offset: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return mirror_uv(r / frame.size + vec2<f32>(0.5) - offset);
}
"""

def cam(slug, name, order, desc, body, params, category="Camera", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + body, params, **kw)

SHAKE_STRUCT = "struct Params { speed: f32, strength: f32 }\n"

PACKAGES = [
cam("shake", "Shake", 10, "The picture shakes as if the camera were jolted.", SHAKE_STRUCT + """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (6.0 + rate() * 8.0));
    let k = params.strength / 100.0;
    let off = (vec2<f32>(hash(vec2<f32>(t, 1.0), 2.0), hash(vec2<f32>(t, 2.0), 2.0)) - vec2<f32>(0.5)) * 0.05 * k;
    return sample(moved(uv, off, 0.0, 1.0 + 0.06 * k));
}
""", [SPEED, p("strength", "Strength", 0, 100, 50)], intensity="strength"),

cam("shake-2", "Shake 2", 11, "A wider shake that rocks the picture back and forth.", SHAKE_STRUCT + """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate() * 6.2831853;
    let k = params.strength / 100.0;
    let off = vec2<f32>(sin(t * 3.1) + 0.5 * sin(t * 7.3), cos(t * 2.7) + 0.5 * sin(t * 5.9)) * 0.025 * k;
    let angle = sin(t * 2.3) * 0.04 * k;
    return sample(moved(uv, off, angle, 1.0 + 0.08 * k));
}
""", [SPEED, p("strength", "Strength", 0, 100, 100)], intensity="strength"),

cam("shake-3", "Shake 3", 12, "A hard shake that splits the picture's colours as it jolts.", SHAKE_STRUCT + """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (6.0 + rate() * 8.0));
    let k = params.strength / 100.0;
    let off = (vec2<f32>(hash(vec2<f32>(t, 1.0), 2.0), hash(vec2<f32>(t, 2.0), 2.0)) - vec2<f32>(0.5)) * 0.06 * k;
    let split = vec2<f32>(off.x * 0.6, off.y * 0.4);
    let r = sample(moved(uv, off + split, 0.0, 1.0 + 0.07 * k));
    let g = sample(moved(uv, off, 0.0, 1.0 + 0.07 * k));
    let b = sample(moved(uv, off - split, 0.0, 1.0 + 0.07 * k));
    return vec4<f32>(r.r, g.g, b.b, g.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 75)], intensity="strength"),

cam("camera-shake", "Camera Shake", 13, "A handheld camera's restless drift and wobble.", SHAKE_STRUCT + """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let k = params.strength / 100.0;
    let off = vec2<f32>(sin(t * 5.1) * 0.6 + sin(t * 11.7) * 0.4, sin(t * 4.3 + 1.0) * 0.6 + sin(t * 9.1) * 0.4) * 0.03 * k;
    let angle = sin(t * 3.7) * 0.02 * k;
    return sample(moved(uv, off, angle, 1.0 + 0.07 * k));
}
""", [SPEED, p("strength", "Range", 0, 100, 15)], intensity="strength"),

cam("jitter", "Jitter", 14, "The picture twitches by a few pixels, frame to frame.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * 24.0);
    let px = params.strength / 100.0 * 12.0;
    let off = (vec2<f32>(hash(vec2<f32>(t, 1.0), 3.0), hash(vec2<f32>(t, 2.0), 3.0)) - vec2<f32>(0.5)) * px / frame.size;
    return sample(moved(uv, off, 0.0, 1.0 + px * 2.0 / frame.size.y));
}
""", [p("strength", "Range", 0, 100, 25)], intensity="strength"),

cam("zoom-lens", "Zoom Lens", 15, "The lens pushes in and pulls back out, again and again.", """
struct Params { speed: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = 0.5 - 0.5 * cos(frame.time * rate() * 3.14159265);
    let z = 1.0 + t * params.range / 100.0;
    return sample(moved(uv, vec2<f32>(0.0), 0.0, z));
}
""", [SPEED, p("range", "Range", 0, 100, 30)], intensity="range"),

cam("mini-zoom", "Mini Zoom", 16, "A slow, steady push in from the start of the clip.", """
struct Params { speed: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = clamp(frame.clip_time / (span() * 2.0), 0.0, 1.0);
    let z = 1.0 + (1.0 - (1.0 - t) * (1.0 - t)) * params.range / 100.0 * 0.4;
    return sample(moved(uv, vec2<f32>(0.0), 0.0, z));
}
""", [SPEED, p("range", "Range", 0, 100, 50)], intensity="range"),

cam("pulse", "Pulse", 17, "The picture swells and settles on a steady pulse.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate());
    let beat = exp(-ph * 6.0);
    let z = 1.0 + beat * 0.08 * params.strength / 100.0;
    let c = sample(moved(uv, vec2<f32>(0.0), 0.0, z));
    return vec4<f32>(c.rgb * (1.0 + beat * 0.15 * params.strength / 100.0), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 60)], intensity="strength"),

cam("heartbeat", "Heartbeat", 18, "A double beat, like a heart: the picture thumps twice, then rests, its edges flushing red.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate() * 0.8);
    let beat = exp(-ph * 14.0) + 0.7 * exp(-max(ph - 0.22, 0.0) * 14.0) * step(0.22, ph);
    let k = params.strength / 100.0;
    let c = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + beat * 0.07 * k));
    let edge = smoothstep(0.3, 0.85, length((uv - vec2<f32>(0.5)) * vec2<f32>(1.2, 1.0)));
    let red = mix(c.rgb, c.rgb * vec3<f32>(1.3, 0.5, 0.5) + vec3<f32>(0.15, 0.0, 0.02), edge * beat * k);
    return vec4<f32>(red, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 70)], intensity="strength", card={"moment": 1.0}),

cam("throb", "Throb", 19, "The picture throbs brighter and larger on a slow beat.", """
struct Params { strength: f32, luminance: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = 0.5 - 0.5 * cos(frame.time * 4.0);
    let k = params.strength / 100.0;
    let c = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + ph * 0.06 * k));
    return vec4<f32>(c.rgb * (1.0 + ph * params.luminance / 100.0 * 0.6), c.a);
}
""", [p("strength", "Strength", 0, 100, 90), p("luminance", "Brightness", 0, 100, 80)], intensity="strength"),

cam("screen-pulse", "Screen Pulse", 20, "Rings of distortion pulse out from the centre with each beat.", """
struct Params { speed: f32, strength: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate());
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let front = ph * (0.4 + params.size / 100.0 * 1.2);
    let ring = exp(-pow((r - front) / 0.06, 2.0)) * (1.0 - ph);
    let k = params.strength / 100.0;
    let push = select(d / r, vec2<f32>(0.0), r < 1e-4) * ring * 0.03 * k;
    let c = sample(uv - push * frame.size.y / frame.size);
    return vec4<f32>(c.rgb * (1.0 + ring * 0.4 * k), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 60), p("size", "Size", 0, 100, 33)], intensity="strength"),

cam("rebound-swing", "Rebound Swing", 21, "The picture swings out and rebounds back, settling with each swing.", """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = fract(frame.time * rate() * 0.5) * 4.0;
    let angle = sin(t * 6.2831853) * exp(-t * 1.2) * 0.25 * params.size / 100.0;
    return sample(moved(uv, vec2<f32>(0.0), angle, 1.0 + abs(angle) * 0.9));
}
""", [SPEED, p("size", "Size", 0, 100, 50)], intensity="size"),

cam("swing", "Swing", 22, "The picture swings gently from side to side like a pendulum.", """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let angle = sin(frame.time * rate() * 3.14159265) * 0.12 * params.size / 100.0;
    let pivot = vec2<f32>(0.0, -0.4 * sin(angle));
    return sample(moved(uv, pivot, angle, 1.0 + abs(angle) * 0.9));
}
""", [SPEED, p("size", "Size", 0, 100, 50)], intensity="size"),

cam("neon-swing", "Neon Swing", 23, "The picture swings while its edges glow neon.", """
struct Params { speed: f32, luminance: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let angle = sin(frame.time * rate() * 3.14159265) * 0.1;
    let q = moved(uv, vec2<f32>(0.0), angle, 1.0 + abs(angle));
    let c = sample(q);
    let e = edge_at(q);
    let hue = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(frame.time * 0.3 + uv.y) + vec3<f32>(0.0, 0.33, 0.67)));
    let neon = hue * hue * e * 3.0 * params.luminance / 100.0;
    return vec4<f32>(c.rgb * (1.0 - e * 0.5) + neon, c.a);
}
""", [SPEED, p("luminance", "Glow", 0, 100, 100)], intensity="luminance"),

cam("dizzy", "Dizzy", 24, "The picture reels and doubles, as if the room were spinning.", """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let k = params.size / 100.0;
    let a = sin(t * 2.0) * 0.08 * k;
    let off = vec2<f32>(sin(t * 1.3), cos(t * 1.7)) * 0.02 * k;
    let one = sample(moved(uv, off, a, 1.08));
    let two = sample(moved(uv, -off, -a, 1.12));
    let c = mix(one, two, 0.4 * k);
    return vec4<f32>(mix(c.rgb, c.rgb * vec3<f32>(1.05, 0.95, 1.1), k * 0.5), c.a);
}
""", [SPEED, p("size", "Size", 0, 100, 70)], intensity="size"),

cam("rotary-focus", "Rotary Focus", 25, "The picture turns with a spinning blur that comes and goes.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let k = params.strength / 100.0 * (0.5 - 0.5 * cos(t * 3.14159265));
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += sample(moved(uv, vec2<f32>(0.0), f32(i) * 0.02 * k, 1.0 + 0.05 * k));
    }
    return sum / 9.0;
}
""", [SPEED, p("strength", "Strength", 0, 100, 100)], intensity="strength"),

cam("flipped", "Flipped", 26, "The picture flips over, left for right, on a beat.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate() * 0.5);
    let w = cos(ph * 6.2831853);
    let x = (uv.x - 0.5) / select(-max(abs(w), 0.02), max(abs(w), 0.02), w >= 0.0) + 0.5;
    if (x < 0.0 || x > 1.0) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let c = sample(vec2<f32>(x, uv.y));
    return vec4<f32>(c.rgb * mix(0.6, 1.0, abs(w)), c.a);
}
""", [SPEED]),

cam("wobbly-black", "Wobbly Black", 27, "A black frame closes in from the edges and wobbles like jelly.", """
struct Params { size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * 2.0;
    let a = atan2(d.y, d.x);
    let wob = 0.04 * sin(a * 5.0 + frame.time * 3.0) + 0.03 * sin(a * 3.0 - frame.time * 2.0);
    let edge = 1.0 - params.size / 100.0 * 0.25 + wob;
    let m = smoothstep(edge, edge - 0.03, max(abs(d.x), abs(d.y)) * 0.9 + length(d) * 0.1);
    return vec4<f32>(c.rgb * m, c.a);
}
""", [p("size", "Size", 0, 100, 60)], intensity="size"),

cam("delay", "Delay", 28, "Ghost copies of the picture trail behind it, out of step.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let k = params.strength / 100.0;
    let c = sample(uv);
    var sum = c.rgb;
    var total = 1.0;
    for (var i = 1; i <= 3; i++) {
        let fi = f32(i);
        let off = vec2<f32>(sin(t * 2.0 - fi * 0.6), cos(t * 1.6 - fi * 0.6)) * 0.015 * fi * k;
        let w = 0.6 / fi;
        sum += sample(uv + off).rgb * w;
        total += w;
    }
    return vec4<f32>(sum / total, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 100)], intensity="strength"),

cam("stuck-frame", "Stuck Frame", 29, "The picture catches and jumps like a projector that keeps slipping.", """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * (1.0 + rate() * 2.0);
    let step_t = floor(t);
    let slip = select(0.0, (hash(vec2<f32>(step_t, 1.0), 4.0) - 0.5) * 0.12, fract(t) < 0.25);
    let q = vec2<f32>(uv.x, fract(uv.y + slip * (0.4 + params.size / 100.0)));
    let c = sample(q);
    let bar = smoothstep(0.015, 0.0, abs(fract(uv.y + slip) - 0.0)) * step(0.001, abs(slip));
    return vec4<f32>(c.rgb * (1.0 - bar), c.a);
}
""", [SPEED, p("size", "Jump", 0, 100, 30)]),

# Openings, closings and flashes.
cam("fade-in", "Fade In", 40, "The clip fades up from black at its start.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = opening();
    return vec4<f32>(c.rgb * t * t, c.a);
}
""", [SPEED], category="Basic", card={"moment": 0.6}),

cam("fade-out", "Fade Out", 41, "The clip fades down to black at its end.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = 1.0 - closing();
    return vec4<f32>(c.rgb * t * t, c.a);
}
""", [SPEED], category="Basic"),

cam("horizontal-open", "Horizontal Open", 42, "Black curtains part from the middle to the sides as the clip begins.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, opening());
    let open = abs(uv.x - 0.5) * 2.0 < t;
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [SPEED], category="Basic", card={"moment": 0.6}),

cam("horizontal-close", "Horizontal Close", 43, "Black curtains close in from the sides to the middle as the clip ends.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = 1.0 - smoothstep(0.0, 1.0, closing());
    let open = abs(uv.x - 0.5) * 2.0 < t;
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [SPEED], category="Basic"),

cam("vertical-open", "Vertical Open", 44, "Black bars part from the middle to the top and bottom as the clip begins.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, opening());
    let open = abs(uv.y - 0.5) * 2.0 < t;
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [SPEED], category="Basic", card={"moment": 0.6}),

cam("vertical-close", "Vertical Close", 45, "Black bars close from the top and bottom to the middle as the clip ends.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = 1.0 - smoothstep(0.0, 1.0, closing());
    let open = abs(uv.y - 0.5) * 2.0 < t;
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [SPEED], category="Basic"),

cam("landscape-close", "Landscape Close", 46, "Black bars slide in to frame the picture in a wide, cinematic strip.", """
struct Params { speed: f32, ratio: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, opening());
    let keep = mix(1.0, (frame.size.x / frame.size.y) / max(params.ratio / 100.0 * 2.0 + 1.5, 1.0), t);
    let open = abs(uv.y - 0.5) * 2.0 < min(keep, 1.0);
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [SPEED, p("ratio", "Width", 0, 100, 40)], category="Basic", card={"moment": 1.0}),

cam("portrait-open", "Portrait Open", 47, "The picture opens out from a tall portrait strip to the full frame.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, opening());
    let start = (frame.size.y * 9.0 / 16.0) / frame.size.x;
    let open = abs(uv.x - 0.5) * 2.0 < mix(min(start, 1.0), 1.0, t);
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [SPEED], category="Basic", card={"moment": 0.4}),

cam("cinema", "Cinema", 48, "Letterbox bars give the picture a widescreen cinema frame.", """
struct Params { ratio: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let target_ratio = mix(1.85, 2.76, params.ratio / 100.0);
    let keep = min((frame.size.x / frame.size.y) / target_ratio, 1.0);
    let open = abs(uv.y - 0.5) * 2.0 < keep;
    return select(vec4<f32>(0.0, 0.0, 0.0, c.a), c, open);
}
""", [p("ratio", "Ratio", 0, 100, 40)], category="Basic"),

cam("the-end", "The End", 49, "An iris closes to black on the picture as the clip ends, the way old films finished.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = 1.0 - smoothstep(0.0, 1.0, closing());
    let d = length((uv - vec2<f32>(0.5)) * frame.size) / (0.5 * length(frame.size));
    let m = smoothstep(t * 1.05, t * 1.05 - 0.02, d);
    let l = luma(c.rgb);
    let old = mix(c.rgb, vec3<f32>(l), 0.6) * vec3<f32>(1.05, 0.98, 0.88);
    return vec4<f32>(old * m, c.a);
}
""", [p("speed", "Speed", 0, 100, 20)], category="Basic"),

cam("blink", "Blink", 50, "The frame blinks like an eye, closing and opening again.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate() * 0.4);
    let close = select(0.0, sin(ph / 0.2 * 3.14159265), ph < 0.2);
    let x = (uv.x - 0.5) * 2.0;
    let lid = close * 0.63 - 0.12 * (1.0 - x * x) * (1.0 - close);
    let m = smoothstep(lid - 0.03, lid, uv.y) * smoothstep(lid - 0.03, lid, 1.0 - uv.y);
    return vec4<f32>(c.rgb * m, c.a);
}
""", [SPEED], category="Basic", card={"moment": 0.2}),

cam("binoculars", "Binoculars", 51, "The picture seen through binoculars, two round lenses on black, drifting as if held.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let drift = vec2<f32>(sin(t * 0.7), cos(t * 0.5)) * 0.02;
    let c = sample(uv + drift);
    let px = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let w = 0.24;
    let r = 0.42;
    let d = min(length(px - vec2<f32>(-w, 0.0)), length(px - vec2<f32>(w, 0.0)));
    let m = smoothstep(r, r - 0.02, d);
    let vig = 1.0 - smoothstep(r * 0.6, r, d) * 0.4;
    return vec4<f32>(c.rgb * m * vig, c.a);
}
""", [SPEED], category="Basic"),

cam("black-flash", "Black Flash", 52, "The picture flashes to black on a beat.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate());
    let k = exp(-ph * 8.0);
    return vec4<f32>(c.rgb * (1.0 - k), c.a);
}
""", [SPEED], category="Light"),

cam("black-flash-2", "Black Flash 2", 53, "Black flashes that buckle the picture as they hit.", """
struct Params { speed: f32, distortion: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate());
    let k = exp(-ph * 8.0);
    let d = uv - vec2<f32>(0.5);
    let bulge = 1.0 + k * params.distortion / 100.0 * 0.4 * dot(d, d);
    let c = sample(vec2<f32>(0.5) + d / bulge);
    return vec4<f32>(c.rgb * (1.0 - k * 0.9), c.a);
}
""", [p("speed", "Speed", 0, 100, 80), p("distortion", "Distortion", 0, 100, 40)], category="Light"),

cam("white-flash", "White Flash", 54, "The picture flashes white on a beat.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate());
    let k = exp(-ph * 8.0);
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0), k), c.a);
}
""", [SPEED], category="Light"),

cam("flash", "Flash", 55, "A camera flash goes off now and then, overexposing the picture for an instant.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate() * 0.5);
    let k = exp(-ph * 14.0);
    return vec4<f32>(c.rgb * (1.0 + k * 5.0) + vec3<f32>(k * 0.5), c.a);
}
""", [SPEED], category="Light"),

cam("white-out", "White Out", 56, "The picture slowly washes out to white.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, clamp(frame.clip_time / (span() * 2.0), 0.0, 1.0));
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0), t * 0.95), c.a);
}
""", [SPEED], category="Light", card={"moment": 1.0}),

cam("low-exposure", "Low Exposure", 57, "The picture breathes darker and back, underexposed.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = 0.5 + 0.5 * sin(frame.time * rate() * 3.14159265);
    return vec4<f32>(exposure(c.rgb, -2.0 * k - 0.5), c.a);
}
""", [SPEED], category="Light"),

cam("to-color", "To Color", 58, "The clip starts in black and white and colour floods into it.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, opening());
    return vec4<f32>(mix(vec3<f32>(luma(c.rgb)), c.rgb, t), c.a);
}
""", [SPEED], category="Color", card={"moment": 0.6}),

cam("flicker", "Flicker", 59, "The light flickers unsteadily, like a failing bulb.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = floor(frame.time * (8.0 + rate() * 8.0));
    let k = mix(0.45, 1.15, hash(vec2<f32>(t, 0.0), 5.0));
    return vec4<f32>(c.rgb * k, c.a);
}
""", [SPEED], category="Light"),

cam("strobe", "Strobe", 60, "A hard strobe flashes the picture on and off.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let on = fract(frame.time * (2.0 + rate() * 4.0)) < 0.5;
    return select(vec4<f32>(c.rgb * 0.08, c.a), vec4<f32>(c.rgb * 1.3, c.a), on);
}
""", [p("speed", "Speed", 0, 100, 100)], category="Party", shelves=["Party & Club"]),

cam("negative-strobe", "Negative Strobe", 61, "The picture strobes between itself and its negative.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let on = fract(frame.time * (2.0 + rate() * 4.0)) < 0.5;
    let d = clamp(to_display(c.rgb), vec3<f32>(0.0), vec3<f32>(1.0));
    let neg = from_display(vec3<f32>(1.0) - d);
    return select(c, vec4<f32>(mix(c.rgb, neg, params.strength / 100.0), c.a), on);
}
""", [p("speed", "Speed", 0, 100, 45), p("strength", "Strength", 0, 100, 85)], category="Party", shelves=["Party & Club"], card={"moment": 0.95}),

cam("blackout", "Blackout", 62, "The picture blurs and sinks into black, then surfaces again.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = (0.5 - 0.5 * cos(frame.time * rate() * 2.0)) * params.strength / 100.0;
    let c = sample(uv);
    let soft = soften(uv, 1.0 + k * 10.0);
    let rgb = mix(c.rgb, soft, k) * (1.0 - k * 0.9);
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 70)], category="Light"),
]
