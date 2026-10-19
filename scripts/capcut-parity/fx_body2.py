from lib_wgsl import *
from fx_camera import SPEED
from fx_body import b, CENTRE, POINT_NOTE

SIZE = p("size", "Size", 0, 100, 50)
S = p("strength", "Strength", 0, 100, 80)

# The point's frame: `d` from the point in frame heights, y down, and the
# size the head is taken to be.
HEAD = """
fn head(uv: vec2<f32>) -> vec2<f32> {
    return (uv - params.centre) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
}

fn head_size() -> f32 {
    return mix(0.08, 0.35, params.size / 100.0);
}

fn from_head(d: vec2<f32>) -> vec2<f32> {
    return params.centre + d / vec2<f32>(frame.size.x / frame.size.y, 1.0);
}
"""

def face(slug, name, order, desc, body, params, **kw):
    return b(slug, name, order, desc + POINT_NOTE, HEAD + body, [CENTRE, SIZE] + params, **kw)

def eyes(shape_expr, tint, glow=True):
    return """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn eye(d: vec2<f32>, s: f32) -> f32 {
    let q = d / s;
    SHAPE
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size();
    let spacing = s * 0.32;
    let beat = 1.0 + 0.1 * sin(frame.time * 6.0);
    let m = max(eye(d - vec2<f32>(-spacing, -s * 0.1), s * 0.18 * beat), eye(d - vec2<f32>(spacing, -s * 0.1), s * 0.18 * beat));
    let k = params.strength / 100.0;
    let tint = TINT;
    let halo = GLOW;
    return vec4<f32>(mix(c.rgb, tint, clamp(m, 0.0, 1.0) * k) + tint * halo * k, c.a);
}
""".replace("SHAPE", shape_expr).replace("TINT", tint).replace("GLOW", "exp(-max(min(length(d - vec2<f32>(-spacing, -s * 0.1)), length(d - vec2<f32>(spacing, -s * 0.1))) - s * 0.15, 0.0) / (s * 0.15)) * 0.6" if glow else "0.0")

HEART_EYE = "let sd = heart_sdf(vec2<f32>(q.x, -q.y)); return smoothstep(0.05, -0.05, sd);"
BOLT_EYE = "let zig = abs(q.x - 0.3 * sign(sin(q.y * 9.0))) ; return smoothstep(0.25, 0.1, zig) * step(abs(q.y), 1.2) + exp(-dot(q, q) * 4.0);"
FLAME_EYE = "let n = fbm(q * 2.0 + vec2<f32>(0.0, frame.time * 3.0)); return smoothstep(1.0, 0.3, length(q * vec2<f32>(1.0, 0.6) + vec2<f32>(0.0, 0.4)) - n * 0.5);"
SHINE_EYE = "return exp(-dot(q, q) * 3.0) + glint(q * 0.25, 0.5) * 0.8;"

ORBIT = """
struct Params { centre: vec2<f32>, size: f32, speed: f32, strength: f32 }

fn sprite(q: vec2<f32>, t: f32) -> f32 {
    SPRITE
}

// Sprites wheeling round the head.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size();
    var m = 0.0;
    for (var i = 0; i < COUNT; i++) {
        let fi = f32(i);
        let a = frame.time * rate() + fi * 6.2831853 / f32(COUNT);
        let at = vec2<f32>(cos(a) * s * 1.2, sin(a) * s * 0.35 - s * RISE);
        m = max(m, sprite((d - at) / (s * 0.22), frame.time + fi));
    }
    let k = params.strength / 100.0;
    let tint = TINT;
    return vec4<f32>(mix(c.rgb, tint, clamp(m, 0.0, 1.0) * k) + tint * m * 0.3 * k, c.a);
}
"""

def orbit(sprite, tint, count=5, rise=0.9):
    return ORBIT.replace("SPRITE", sprite).replace("TINT", tint).replace("COUNT", str(count)).replace("RISE", f"{rise}")

STAR_SPRITE = "let r = length(q); let a = atan2(q.x, -q.y); let k = abs(fract(a / 1.2566371 + 0.5) - 0.5) * 2.0; return smoothstep(mix(0.42, 1.0, pow(1.0 - k, 2.0)), mix(0.42, 1.0, pow(1.0 - k, 2.0)) - 0.1, r);"
HEART_SPRITE = "return smoothstep(0.05, -0.05, heart_sdf(vec2<f32>(q.x, -q.y)));"
NOTE_SPRITE = "let head = smoothstep(1.0, 0.85, length((q - vec2<f32>(-0.2, 0.55)) * vec2<f32>(2.4, 3.2))); let stem = step(abs(q.x - 0.18), 0.06) * step(-0.8, q.y) * step(q.y, 0.55); return max(head, stem);"
FLAME_SPRITE = "let n = fbm(q * 1.5 + vec2<f32>(0.0, t * 3.0)); return smoothstep(1.0, 0.3, length(q * vec2<f32>(1.0, 0.6) + vec2<f32>(0.0, 0.3)) - n * 0.6);"
ARROW_SPRITE = "let shaft = step(abs(q.y), 0.12) * step(-0.9, q.x) * step(q.x, 0.3); let tip = step(abs(q.y), 0.6 - (q.x - 0.3) * 1.0) * step(0.3, q.x) * step(q.x, 0.9); return max(shaft, tip);"

def wings(tint, flame):
    fill = "fbm(q * 3.0 + vec2<f32>(0.0, frame.time * 2.0))" if flame else "0.7 + 0.3 * sin(q.y * 30.0)"
    return """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

// A pair of wings spread behind the subject, beating slowly.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv) - vec2<f32>(0.0, head_size() * 1.6);
    let s = head_size() * 2.2;
    let beat = 0.85 + 0.15 * sin(frame.time * 3.0);
    let q = vec2<f32>(abs(d.x) / (s * beat), d.y / s);
    let upper = smoothstep(1.0, 0.85, length((q - vec2<f32>(0.6, -0.35)) * vec2<f32>(1.4, 2.0)));
    let lower = smoothstep(1.0, 0.85, length((q - vec2<f32>(0.45, 0.2)) * vec2<f32>(2.0, 2.6)));
    let wing = max(upper, lower) * step(0.12, q.x) * (FILL);
    let k = params.strength / 100.0;
    let tint = TINT;
    return vec4<f32>(mix(c.rgb, tint, clamp(wing, 0.0, 1.0) * 0.8 * k) + tint * wing * 0.3 * k, c.a);
}
""".replace("FILL", fill).replace("TINT", tint)

BOLTS = """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

// Jagged bolts of electricity crackle out from round the subject.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size();
    let a = atan2(d.y, d.x);
    let r = length(d);
    let t = floor(frame.time * 12.0);
    let n = BOLTCOUNT;
    let sector = floor((a / 6.2831853 + 0.5) * n);
    let centre_a = (sector + 0.5) / n * 6.2831853 - 3.14159265;
    let wiggle = (vnoise(vec2<f32>(r * 30.0, sector + t)) - 0.5) * 0.25;
    let off = abs(a - centre_a - wiggle) * r;
    let live = step(0.4, hash(vec2<f32>(sector, t), 1.0)) * smoothstep(s * 0.8, s, r) * smoothstep(s * REACH, s, r);
    let bolt = 0.002 / (off + 0.002) * live;
    let k = params.strength / 100.0;
    return vec4<f32>(c.rgb + TINT * bolt * 2.0 * k, c.a);
}
"""

def bolts(tint, count=10, reach=3.0):
    return BOLTS.replace("TINT", tint).replace("BOLTCOUNT", f"{float(count)}").replace("REACH", f"{reach}")

PACKAGES = [
face("big-head", "Big Head", 40, "A bobble-head: the head swells up big.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = head(uv);
    let s = head_size() * 1.5;
    let r = length(d) / s;
    let k = params.strength / 100.0 * 0.6;
    let pull = select(1.0, 1.0 - k * (1.0 - r * r), r < 1.0);
    return sample(from_head(d * pull));
}
""", [S], intensity="strength"),
face("big-mouth", "Big Mouth", 41, "The mouth swells comically large.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let mouth = vec2<f32>(0.0, head_size() * 0.45);
    let d = head(uv) - mouth;
    let s = head_size() * 0.6;
    let r = length(d * vec2<f32>(0.8, 1.2)) / s;
    let k = params.strength / 100.0 * 0.6;
    let pull = select(1.0, 1.0 - k * (1.0 - r * r), r < 1.0);
    return sample(from_head(d * pull + mouth));
}
""", [S], intensity="strength"),
face("face-mosaic", "Face Mosaic", 42, "The face hidden behind mosaic blocks.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = head(uv);
    let s = head_size();
    if (length(d * vec2<f32>(1.0, 0.8)) > s) {
        return sample(uv);
    }
    let px = mix(6.0, 40.0, params.strength / 100.0);
    let cells = frame.size / px;
    return sample((floor(uv * cells) + vec2<f32>(0.5)) / cells);
}
""", [p("strength", "Block size", 0, 100, 50)]),
face("face-glitch", "Face Glitch", 43, "The face glitches and splits while the rest stays still.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = head(uv);
    let s = head_size();
    let inside = smoothstep(s * 1.1, s * 0.9, length(d * vec2<f32>(1.0, 0.8)));
    let t = floor(frame.time * 12.0);
    let row = floor(uv.y * 60.0);
    let tear = (hash(vec2<f32>(row, t), 1.0) - 0.5) * 0.05 * inside * params.strength / 100.0;
    let o = vec2<f32>(0.008 * inside * params.strength / 100.0, 0.0);
    let g = sample(uv + vec2<f32>(tear, 0.0));
    return vec4<f32>(sample(uv + vec2<f32>(tear, 0.0) + o).r, g.g, sample(uv + vec2<f32>(tear, 0.0) - o).b, g.a);
}
""", [S], intensity="strength"),
face("phantom-face", "Phantom Face", 44, "A ghostly double of the face floats off and fades.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let s = head_size();
    let drift = vec2<f32>(sin(frame.time) * s * 0.4, -s * 0.3 - s * 0.2 * sin(frame.time * 0.7));
    let d = head(uv) - drift;
    let mask = smoothstep(s * 1.1, s * 0.6, length(d * vec2<f32>(1.0, 0.8)));
    let ghost = sample(from_head(d));
    return vec4<f32>(c.rgb + ghost.rgb * vec3<f32>(0.6, 0.8, 1.2) * mask * 0.5 * params.strength / 100.0, c.a);
}
""", [S], intensity="strength"),
face("embarrassed-face", "Embarrassed Face", 45, "Rosy blushes bloom on the cheeks, with little worry lines.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size();
    let cheek = exp(-dot(d - vec2<f32>(-s * 0.4, s * 0.2), d - vec2<f32>(-s * 0.4, s * 0.2)) / (s * s * 0.03))
        + exp(-dot(d - vec2<f32>(s * 0.4, s * 0.2), d - vec2<f32>(s * 0.4, s * 0.2)) / (s * s * 0.03));
    let lines = step(0.5, fract(d.x / (s * 0.08))) * step(abs(d.y + s * 0.95), s * 0.12) * step(abs(d.x - s * 0.6), s * 0.2);
    let k = params.strength / 100.0;
    let rgb = mix(c.rgb, vec3<f32>(1.0, 0.35, 0.45), clamp(cheek * 0.6, 0.0, 1.0) * k);
    return vec4<f32>(mix(rgb, vec3<f32>(0.1), lines * k), c.a);
}
""", [S], intensity="strength"),
face("sad", "Sad", 46, "A blue, gloomy cast with tears running down from the eyes.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size();
    let k = params.strength / 100.0;
    var tear = 0.0;
    for (var i = 0; i < 2; i++) {
        let x = select(-s * 0.32, s * 0.32, i == 1);
        let flow = fract(frame.time * 0.8 + f32(i) * 0.4);
        let along = d.y + s * 0.05;
        let drop = exp(-pow((d.x - x) / (s * 0.04), 2.0)) * step(0.0, along) * step(along, s * 0.9 * flow + s * 0.1);
        tear += drop;
    }
    let gloom = mix(c.rgb, vec3<f32>(luma(c.rgb)) * vec3<f32>(0.75, 0.85, 1.1), 0.5 * k);
    return vec4<f32>(mix(gloom, vec3<f32>(0.6, 0.85, 1.3), clamp(tear, 0.0, 1.0) * 0.7 * k), c.a);
}
""", [S], intensity="strength"),
face("cool-shades", "Cool", 47, "Pixel sunglasses drop down onto the face.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let s = head_size();
    let drop = (1.0 - smoothstep(0.0, 0.6, fract(frame.time * 0.25) * 4.0)) * s * 2.0;
    let d = head(uv) - vec2<f32>(0.0, -s * 0.1 - drop);
    let px = floor(d / (s * 0.06));
    let lens = (abs(px.x + 5.0) <= 3.0 || abs(px.x - 5.0) <= 3.0) && px.y >= -1.0 && px.y <= 2.0 - abs(px.x) * 0.0;
    let bridge = abs(px.x) <= 2.0 && px.y == -1.0;
    let glint_at = (px.x == -7.0 || px.x == 3.0) && px.y == 0.0;
    var rgb = c.rgb;
    rgb = select(rgb, vec3<f32>(0.02), lens || bridge);
    rgb = select(rgb, vec3<f32>(1.0), glint_at && lens);
    return vec4<f32>(mix(c.rgb, rgb, params.strength / 100.0), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)]),
face("lovestruck", "Lovestruck", 48, "Hearts beat in place of the eyes.", eyes(HEART_EYE, "vec3<f32>(1.0, 0.1, 0.3)"), [S], intensity="strength"),
face("heart-lenses", "Heart Lenses", 49, "Heart-shaped glasses over the eyes.", eyes("let sd = heart_sdf(vec2<f32>(q.x, -q.y) * 0.8); return smoothstep(0.08, 0.0, abs(sd)) + smoothstep(0.0, -0.05, sd) * 0.35;", "vec3<f32>(1.0, 0.3, 0.55)", glow=False), [S], intensity="strength"),
face("loving-gaze", "Loving Gaze", 50, "Soft pink hearts glow in the eyes.", eyes(HEART_EYE, "vec3<f32>(1.0, 0.55, 0.75)"), [S], intensity="strength"),
face("lightning-eyes", "Lightning Eyes", 51, "Bolts of lightning crackle from the eyes.", eyes(BOLT_EYE, "vec3<f32>(0.6, 0.8, 1.6)"), [S], intensity="strength"),
face("flame-eyes", "Flame Eyes", 52, "Flames burn in the eyes.", eyes(FLAME_EYE, "vec3<f32>(1.8, 0.6, 0.1)"), [S], intensity="strength"),
face("eye-reflection", "Eye Reflection", 53, "Sparkling highlights glint in the eyes.", eyes(SHINE_EYE, "vec3<f32>(1.0, 1.0, 1.0)"), [S], intensity="strength"),
face("in-my-heart", "In My Heart", 54, "The subject framed inside a big pink heart, the rest softened.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size() * 3.0 * (1.0 + 0.04 * sin(frame.time * 5.0));
    let sd = heart_sdf(vec2<f32>(d.x, -d.y) / s);
    let k = params.strength / 100.0;
    let outside = smoothstep(-0.02, 0.02, sd);
    let rim = exp(-abs(sd) / 0.015);
    let rgb = mix(c.rgb, mix(c.rgb, vec3<f32>(1.0, 0.75, 0.85), 0.6), outside * k) + vec3<f32>(1.0, 0.3, 0.5) * rim * k;
    return vec4<f32>(rgb, c.a);
}
""", [S], category="Love", intensity="strength"),
face("bright-idea", "Bright Idea", 55, "A light bulb pops on above the head.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let s = head_size();
    let d = head(uv) - vec2<f32>(0.0, -s * 1.6);
    let on = smoothstep(0.0, 0.1, fract(frame.time * 0.5));
    let bulb = smoothstep(s * 0.42, s * 0.38, length(d));
    let base = step(abs(d.x), s * 0.18) * step(s * 0.38, d.y) * step(d.y, s * 0.62);
    let rays = pow(max(0.0, sin(atan2(d.y, d.x) * 10.0)), 10.0) * smoothstep(s * 1.2, s * 0.5, length(d)) * step(s * 0.5, length(d));
    let k = params.strength / 100.0;
    var rgb = mix(c.rgb, vec3<f32>(1.4, 1.2, 0.4) * on + vec3<f32>(0.3) * (1.0 - on), bulb * k);
    rgb = mix(rgb, vec3<f32>(0.5), base * k);
    rgb = rgb + vec3<f32>(1.0, 0.9, 0.3) * rays * on * k;
    return vec4<f32>(rgb, c.a);
}
""", [S], category="Fun", intensity="strength"),
face("struck", "Struck", 56, "Stars spin round the head as if knocked silly.", orbit("""let r = length(q); let a = atan2(q.x, -q.y); let k = abs(fract(a / 1.2566371 + 0.5) - 0.5) * 2.0; return smoothstep(mix(0.42, 1.0, pow(1.0 - k, 2.0)), mix(0.42, 1.0, pow(1.0 - k, 2.0)) - 0.1, r);""", "vec3<f32>(1.0, 0.85, 0.15)"), [SPEED, S], category="Fun", intensity="strength"),
face("musical-notes-2", "Musical Notes 2", 57, "Musical notes circle the head.", orbit(NOTE_SPRITE, "vec3<f32>(1.0)", count=4), [SPEED, S], category="Fun", intensity="strength"),
face("club-hearts", "Club Hearts", 58, "Hearts in party colours circle the head.", orbit(HEART_SPRITE, "rainbow(fract(frame.time * 0.3))", count=6), [SPEED, S], category="Love", intensity="strength"),
face("revolving-flames", "Revolving Flames", 59, "Flames circle round the subject.", orbit(FLAME_SPRITE, "vec3<f32>(1.8, 0.6, 0.1)", count=6, rise=0.0), [SPEED, S], intensity="strength"),
face("looping-arrows", "Looping Arrows", 60, "Arrows loop round and round the subject.", orbit(ARROW_SPRITE, "vec3<f32>(1.0, 0.9, 0.2)", count=4, rise=0.0), [SPEED, S], category="Fun", intensity="strength"),
face("heart-flames", "Heart Flames", 61, "Flaming hearts circle the head.", orbit(HEART_SPRITE + "", "vec3<f32>(1.6, 0.35, 0.15)", count=5), [SPEED, S], category="Love", intensity="strength"),
face("butterfly-wings", "Butterfly Wings", 62, "Shimmering butterfly wings spread behind the subject.", wings("rainbow(fract(q.y * 0.5 + frame.time * 0.1))", False), [S], intensity="strength"),
face("flame-wings-1", "Flame Wings 1", 63, "Wings of fire spread behind the subject.", wings("vec3<f32>(1.8, 0.6, 0.1)", True), [S], intensity="strength"),
face("flame-wings-2", "Flame Wings 2", 64, "Wings of blue fire spread behind the subject.", wings("vec3<f32>(0.3, 0.6, 1.8)", True), [S], intensity="strength"),
face("electric-shock", "Electric Shock", 65, "Electricity crackles round the subject.", bolts("vec3<f32>(0.6, 0.8, 1.8)"), [S], intensity="strength"),
face("electric-storm", "Electric Storm", 66, "A storm of bolts lashes out round the subject on a darker picture.", bolts("vec3<f32>(0.8, 0.6, 1.8)", count=16, reach=5.0), [S], intensity="strength"),
face("radiate-bolts", "Radiate Bolts", 67, "Golden bolts radiate out from the subject.", bolts("vec3<f32>(1.8, 1.3, 0.3)", count=12, reach=4.0), [S], intensity="strength"),
face("lightning-bound", "Lightning Bound", 68, "A ring of lightning binds the subject.", bolts("vec3<f32>(0.7, 0.9, 1.8)", count=24, reach=1.6), [S], intensity="strength"),
face("crackling", "Crackling", 69, "Short sparks crackle close around the subject.", bolts("vec3<f32>(1.6, 1.2, 0.8)", count=30, reach=1.4), [S], intensity="strength"),
face("halo-ring", "Halo Ring", 70, "A glowing halo floats above the head.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let s = head_size();
    let d = head(uv) - vec2<f32>(0.0, -s * 1.25 + sin(frame.time * 2.0) * s * 0.05);
    let ring = exp(-pow((length(d * vec2<f32>(1.0, 3.5)) - s * 0.7) / (s * 0.06), 2.0));
    return vec4<f32>(c.rgb + vec3<f32>(1.4, 1.2, 0.6) * ring * params.strength / 100.0 * 1.5, c.a);
}
""", [S], intensity="strength"),
face("tyndall-effect", "Tyndall Effect", 71, "Shafts of light pour down through haze onto the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let src = vec2<f32>(params.centre.x + 0.25, -0.1);
    let d = (uv - src) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let a = atan2(d.x, d.y);
    let rays = pow(0.5 + 0.5 * sin(a * 40.0 + frame.time * 0.3), 4.0) * 0.5 + 0.5 * fbm(vec2<f32>(a * 10.0, frame.time * 0.1));
    let k = params.strength / 100.0 * smoothstep(1.2, 0.0, length(d));
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.95, 0.8) * rays * k * 0.6, c.a);
}
""", [S], category="Light", intensity="strength"),
face("starlight", "Starlight", 72, "Stars twinkle into a glow around the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size();
    let cells = vec2<f32>(24.0, 24.0 * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let near = smoothstep(s * 4.0, s, length(d));
    let star = glint(fract(uv * cells) - vec2<f32>(0.5), 0.6) * step(0.85, hash(cell, 1.0)) * (0.5 + 0.5 * sin(frame.time * 4.0 + hash(cell, 2.0) * 6.28)) * near;
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.95, 0.8) * star * 1.5 * params.strength / 100.0, c.a);
}
""", [S], category="Sparkle", intensity="strength"),
face("hurricane", "Hurricane", 73, "A whirlwind of streaks spins round the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv) * vec2<f32>(1.0, 2.5);
    let s = head_size() * 2.5;
    let r = length(d);
    let a = atan2(d.y, d.x) - frame.time * 4.0 + r * 8.0;
    let streak = pow(0.5 + 0.5 * sin(a * 6.0), 12.0) * smoothstep(s * 1.6, s, r) * smoothstep(s * 0.5, s, r);
    return vec4<f32>(c.rgb + vec3<f32>(0.85, 0.9, 1.0) * streak * params.strength / 100.0, c.a);
}
""", [S], intensity="strength"),
face("distorted-whirl", "Distorted Whirl", 74, "The picture whirls and bends around the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = head(uv);
    let s = head_size() * 3.0;
    let r = length(d);
    let a = params.strength / 100.0 * 2.0 * smoothstep(s, s * 0.3, r) * sin(frame.time * 1.5);
    let q = vec2<f32>(d.x * cos(a) - d.y * sin(a), d.x * sin(a) + d.y * cos(a));
    return sample(from_head(q));
}
""", [S], intensity="strength"),
face("gas-flow", "Gas Flow", 75, "Coloured smoke flows up around the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let n = fbm(uv * 4.0 + vec2<f32>(0.0, frame.time * 0.6));
    let near = smoothstep(head_size() * 5.0, head_size() * 1.5, length(d));
    let smoke = smoothstep(0.5, 0.8, n) * near;
    let tint = rainbow(fract(n + frame.time * 0.05));
    return vec4<f32>(mix(c.rgb, tint, smoke * 0.6 * params.strength / 100.0), c.a);
}
""", [S], intensity="strength"),
face("gas-waves", "Gas Waves", 76, "Waves of glowing gas ripple outward from the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let r = length(head(uv));
    let n = fbm(uv * 5.0 + vec2<f32>(frame.time * 0.3));
    let waves = pow(0.5 + 0.5 * sin(r * 30.0 - frame.time * 3.0 + n * 4.0), 6.0) * smoothstep(head_size() * 5.0, head_size(), r);
    return vec4<f32>(c.rgb + vec3<f32>(0.4, 1.0, 0.9) * waves * 0.6 * params.strength / 100.0, c.a);
}
""", [S], intensity="strength"),
face("sound-wave", "Sound Wave", 77, "Bars of a sound visualiser pulse up behind the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let bars = 40.0;
    let i = floor(uv.x * bars);
    let level = 0.15 + 0.35 * vnoise(vec2<f32>(i * 0.7, frame.time * 6.0)) * (1.0 - abs(uv.x - params.centre.x));
    let local = fract(uv.x * bars);
    let bar = step(0.2, local) * step(local, 0.8) * step(1.0 - level, uv.y);
    let tint = rainbow(i / bars);
    return vec4<f32>(mix(c.rgb, tint, bar * 0.8 * params.strength / 100.0), c.a);
}
""", [S], category="Party", intensity="strength"),
face("geometric-lasers", "Geometric Lasers", 78, "Laser beams sweep in geometric patterns from behind the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv) - vec2<f32>(0.0, head_size() * 2.0);
    var light = 0.0;
    for (var i = 0; i < 6; i++) {
        let a = frame.time * (0.5 + f32(i) * 0.1) + f32(i) * 1.047;
        let n = vec2<f32>(-sin(a), cos(a));
        light += exp(-abs(dot(d, n)) / 0.003) * step(0.0, dot(d, vec2<f32>(cos(a), sin(a))));
    }
    return vec4<f32>(c.rgb + vec3<f32>(0.3, 1.5, 0.6) * light * params.strength / 100.0, c.a);
}
""", [S], category="Party", intensity="strength"),
face("scan", "Scan", 79, "A scanning beam sweeps up and down the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let pos = 0.5 + 0.45 * sin(frame.time * 1.5);
    let line = exp(-pow((uv.y - pos) / 0.004, 2.0));
    let grid = step(0.95, fract(uv.x * 40.0)) + step(0.95, fract(uv.y * 40.0 * frame.size.y / frame.size.x));
    let near = smoothstep(head_size() * 4.0, head_size(), length(head(uv)));
    let k = params.strength / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(0.2, 1.4, 1.6) * (line + grid * 0.15 * near) * k, c.a);
}
""", [S], intensity="strength"),
face("scan-2", "Scan 2", 80, "A holographic scan ring travels down the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let pos = fract(frame.time * 0.5) * head_size() * 6.0 - head_size() * 1.5;
    let ring = exp(-pow((length(vec2<f32>(d.x, (d.y - pos) * 4.0)) - head_size() * 1.2) / 0.006, 2.0));
    let below = step(d.y, pos) * smoothstep(head_size() * 2.0, head_size() * 0.8, abs(d.x));
    let k = params.strength / 100.0;
    return vec4<f32>(mix(c.rgb, c.rgb * vec3<f32>(0.6, 1.1, 1.3), below * 0.4 * k) + vec3<f32>(0.3, 1.2, 1.6) * ring * k, c.a);
}
""", [S], intensity="strength"),
face("technology-2", "Technology 2", 81, "A tech HUD of rings and ticks locks on to the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let s = head_size() * 1.4;
    let r = length(d);
    let a = atan2(d.y, d.x);
    let ring1 = exp(-abs(r - s) / 0.002) * step(0.3, fract(a / 6.2831853 * 3.0 + frame.time * 0.2));
    let ring2 = exp(-abs(r - s * 1.2) / 0.002) * step(0.5, fract(a / 6.2831853 * 24.0 - frame.time * 0.5));
    let k = params.strength / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(0.2, 1.0, 1.6) * (ring1 + ring2) * k, c.a);
}
""", [S], intensity="strength"),
face("mechanical", "Mechanical", 82, "Turning cogs and a metallic sheen give the subject a machine look.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv) - vec2<f32>(head_size() * 1.3, -head_size());
    let r = length(d);
    let a = atan2(d.y, d.x) + frame.time;
    let teeth = step(0.5, fract(a / 6.2831853 * 12.0));
    let cog = step(r, head_size() * (0.4 + 0.06 * teeth)) * step(head_size() * 0.15, r);
    let l = luma(c.rgb);
    let metal = vec3<f32>(l) * vec3<f32>(0.9, 0.95, 1.05) + vec3<f32>(pow(l, 4.0));
    let k = params.strength / 100.0;
    return vec4<f32>(mix(mix(c.rgb, metal, 0.5 * k), vec3<f32>(0.7, 0.72, 0.75), cog * k), c.a);
}
""", [S], intensity="strength"),
face("totem-flames", "Totem Flames", 83, "A column of fire rises up behind the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let n = fbm(vec2<f32>(d.x * 8.0, d.y * 4.0 + frame.time * 3.0));
    let column = smoothstep(head_size() * 1.8, head_size() * 0.6, abs(d.x) + n * head_size());
    let tint = mix(vec3<f32>(1.2, 0.2, 0.02), vec3<f32>(3.0, 1.6, 0.4), column);
    return vec4<f32>(mix(c.rgb, tint, column * 0.7 * params.strength / 100.0), c.a);
}
""", [S], intensity="strength"),
face("hellfire", "Hellfire", 84, "Hellish red fire engulfs everything around the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = head(uv);
    let n = fbm(vec2<f32>(uv.x * 5.0, uv.y * 3.0 + frame.time * 2.5));
    let away = smoothstep(head_size() * 1.5, head_size() * 4.0, length(d * vec2<f32>(1.0, 0.6)));
    let fire = smoothstep(0.35, 0.75, n + (uv.y - 0.5) * 0.6) * away;
    let tint = mix(vec3<f32>(0.8, 0.05, 0.02), vec3<f32>(2.5, 0.8, 0.1), fire);
    let red = c.rgb * vec3<f32>(1.2, 0.6, 0.5);
    return vec4<f32>(mix(red, tint, fire * params.strength / 100.0), c.a);
}
""", [S], intensity="strength"),
face("firework-burst", "Firework", 85, "A firework bursts behind the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let life = fract(frame.time * 0.6);
    let d = head(uv) - vec2<f32>(0.0, -head_size() * 2.0);
    let r = length(d);
    let a = atan2(d.y, d.x);
    let spoke = smoothstep(0.08, 0.0, abs(fract(a / 6.2831853 * 20.0) - 0.5) - 0.42);
    let spark = spoke * exp(-abs(r - life * head_size() * 4.0) / 0.01) * (1.0 - life);
    let tint = rainbow(floor(frame.time * 0.6) * 0.37);
    return vec4<f32>(c.rgb + tint * spark * 3.0 * params.strength / 100.0, c.a);
}
""", [S], category="Party", intensity="strength"),
face("heart-background", "Heart Background", 86, "Soft pink hearts float behind the subject.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let cells = vec2<f32>(6.0, 6.0 * frame.size.y / frame.size.x);
    let q = vec2<f32>(uv.x, uv.y + frame.time * 0.05) * cells;
    let cell = floor(q);
    let f = fract(q) - vec2<f32>(0.5);
    let m = smoothstep(0.05, -0.05, heart_sdf(vec2<f32>(f.x, -f.y) * 3.0)) * step(0.4, hash(cell, 1.0));
    let away = smoothstep(head_size() * 1.2, head_size() * 3.0, length(head(uv)));
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0, 0.5, 0.7), m * away * 0.7 * params.strength / 100.0), c.a);
}
""", [S], category="Love", intensity="strength"),
face("like-burst", "Like", 87, "Little hearts pop up and float away from the subject.", orbit(HEART_SPRITE, "vec3<f32>(1.0, 0.2, 0.4)", count=7, rise=1.4), [SPEED, S], category="Love", intensity="strength"),
face("axis-rotation-fx", "Axis Rotation", 88, "The picture swings back and forth about its vertical axis, as if on a turntable.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let theta = sin(frame.time * 1.5) * 0.9 * params.strength / 100.0;
    let cx = uv.x - params.centre.x;
    let den = cos(theta) - cx * sin(theta) * 0.8;
    let lx = cx / den;
    let q = vec2<f32>(lx + params.centre.x, (uv.y - 0.5) * (1.0 + lx * sin(theta) * 0.8) + 0.5);
    if (q.x < 0.0 || q.x > 1.0 || q.y < 0.0 || q.y > 1.0) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    return sample(q);
}
""", [S], intensity="strength"),
]
