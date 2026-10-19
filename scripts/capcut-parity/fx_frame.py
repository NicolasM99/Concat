from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

def fr(slug, name, order, desc, body, params, category="Frame", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + NOISE + RAINBOW + HEART + body, params, **kw)

# Distance in frame heights from `uv` to the frame's edge, inset by `inset`.
EDGE = """
fn edge_distance(uv: vec2<f32>) -> f32 {
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    return min(min(px.x, w - px.x), min(px.y, 1.0 - px.y));
}
"""

def grid(cols, rows, mirror=False):
    flip = """
    if (MIRROR && (i32(cell.x) % 2 == 1)) {
        local.x = 1.0 - local.x;
    }""".replace("MIRROR", "true" if mirror else "false")
    return """
struct Params { gap: f32 }

// The picture repeated in a grid, each copy the whole picture scaled to fit
// its cell, a thin gap between them.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let cells = vec2<f32>(COLS, ROWS);
    let cell = floor(uv * cells);
    var local = fract(uv * cells);
    let g = params.gap / 100.0 * 0.04 * cells;
    if (any(local < g * 0.5) || any(local > vec2<f32>(1.0) - g * 0.5)) {
        return vec4<f32>(1.0, 1.0, 1.0, 1.0);
    }
    local = (local - g * 0.5) / (vec2<f32>(1.0) - g);
    // Fill the cell from the middle of the picture, keeping its aspect.
    let cell_aspect = (frame.size.x / cells.x) / (frame.size.y / cells.y);
    let pic_aspect = frame.size.x / frame.size.y;
    var q = local - vec2<f32>(0.5);
    if (cell_aspect < pic_aspect) {
        q.x = q.x * cell_aspect / pic_aspect;
    } else {
        q.y = q.y * pic_aspect / cell_aspect;
    }
    local = q + vec2<f32>(0.5);FLIP
    return sample(local);
}
""".replace("COLS", f"{float(cols)}").replace("ROWS", f"{float(rows)}").replace("FLIP", flip)

GAP = [p("gap", "Border", 0, 100, 0)]

PACKAGES = [
fr("dual-screens", "Dual Screens", 10, "The picture twice, side by side.", grid(2, 1), GAP, category="Split"),
fr("three-screens", "Three Screens", 11, "The picture three times, stacked.", grid(1, 3), GAP, category="Split"),
fr("four-screens", "Four Screens", 12, "The picture four times, in a two-by-two grid.", grid(2, 2), GAP, category="Split"),
fr("six-screens", "Six Screens", 13, "The picture six times, in a grid of three by two.", grid(3, 2), GAP, category="Split"),
fr("nine-screens", "Nine Screens", 14, "The picture nine times, in a three-by-three grid.", grid(3, 3), GAP, category="Split"),
fr("mirror-fx", "Mirror", 15, "The left half of the picture mirrored onto the right.", """
struct Params { axis: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    if (params.axis < 0.5) {
        return sample(vec2<f32>(select(uv.x, 1.0 - uv.x, uv.x > 0.5), uv.y));
    }
    return sample(vec2<f32>(uv.x, select(uv.y, 1.0 - uv.y, uv.y > 0.5)));
}
""", [p("axis", "Axis", 0, 1, 0, values=[0, 1], labels=["Left to right", "Top to bottom"])], category="Split"),
fr("tri-layer-mirror", "Tri-layer Mirror", 16, "Three bands of the picture, the outer two mirrored and dimmed.", """
struct Params { shift: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let band = floor(uv.y * 3.0);
    let local = fract(uv.y * 3.0);
    let off = (params.shift / 100.0 - 0.5) * 0.3;
    let y = 0.5 + (local - 0.5) / 3.0 * 3.0 * 0.333 + off * (band - 1.0);
    var q = vec2<f32>(uv.x, clamp(0.333 + local * 0.333 + off * (band - 1.0), 0.0, 1.0));
    if (band != 1.0) {
        q.x = 1.0 - q.x;
    }
    let c = sample(q);
    let dim = select(0.65, 1.0, band == 1.0);
    return vec4<f32>(c.rgb * dim + vec3<f32>(y * 0.0), c.a);
}
""", [p("shift", "Shift", 0, 100, 50)], category="Split"),
fr("split-screen", "Split Screen", 17, "The picture split into strips that slide against each other.", """
struct Params { speed: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let strip = floor(uv.x * 3.0);
    let dir = select(1.0, -1.0, strip == 1.0);
    let shift = sin(frame.time * rate() * 2.0) * params.range / 100.0 * dir;
    return sample(vec2<f32>(uv.x, fract(uv.y + shift)));
}
""", [SPEED, p("range", "Range", 0, 100, 10)], category="Split"),

fr("film-frame", "Film Frame", 20, "The picture inside a strip of film, sprocket holes down both sides.", EDGE + """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let border = 0.09;
    if (px.x < border || px.x > w - border) {
        let local = select(px.x, w - px.x, px.x > w * 0.5);
        let hole = abs(local - border * 0.5) < border * 0.22 && abs(fract(px.y * 10.0 + frame.time * 0.0) - 0.5) < 0.22;
        return select(vec4<f32>(0.04, 0.04, 0.04, 1.0), vec4<f32>(0.9, 0.9, 0.85, 1.0), hole);
    }
    let q = vec2<f32>((px.x - border) / (w - 2.0 * border), uv.y);
    return sample(q);
}
""", [], category="Frame"),
fr("film-frame-2", "Film Frame 2", 21, "The picture as a frame on a rolling strip of film, its edge numbers showing.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let roll = frame.time * 0.15;
    let border = 0.08;
    let y = fract(uv.y + roll);
    if (px.x < border || px.x > w - border) {
        let local = select(px.x, w - px.x, px.x > w * 0.5);
        let hole = abs(local - border * 0.5) < border * 0.25 && abs(fract(y * 12.0) - 0.5) < 0.2;
        return select(vec4<f32>(0.25, 0.12, 0.03, 1.0), vec4<f32>(0.95, 0.9, 0.8, 1.0), hole);
    }
    if (abs(fract(y) - 0.0) < 0.012 || abs(fract(y) - 1.0) < 0.012) {
        return vec4<f32>(0.03, 0.03, 0.03, 1.0);
    }
    let q = vec2<f32>((px.x - border) / (w - 2.0 * border), y);
    let c = sample(q);
    return vec4<f32>(c.rgb * vec3<f32>(1.05, 0.98, 0.88), c.a);
}
""", [], category="Frame"),
fr("rolling-film", "Rolling Film", 22, "The picture rolls by on a film strip as through a projector gate.", """
struct Params { speed: f32, look: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let border = 0.08;
    let y = uv.y + frame.time * rate() * 0.3;
    if (px.x < border || px.x > w - border) {
        let local = select(px.x, w - px.x, px.x > w * 0.5);
        let hole = abs(local - border * 0.5) < border * 0.25 && abs(fract(y * 12.0) - 0.5) < 0.2;
        return select(vec4<f32>(0.04, 0.04, 0.04, 1.0), vec4<f32>(0.9, 0.9, 0.85, 1.0), hole);
    }
    let local_y = fract(y * 1.25);
    if (local_y > 0.94) {
        return vec4<f32>(0.04, 0.04, 0.04, 1.0);
    }
    let q = vec2<f32>((px.x - border) / (w - 2.0 * border), local_y / 0.94);
    let c = sample(q);
    let l = luma(c.rgb);
    return vec4<f32>(mix(c.rgb, vec3<f32>(l * 1.05, l * 0.95, l * 0.8), params.look / 100.0), c.a);
}
""", [p("speed", "Speed", 0, 100, 50), p("look", "Sepia", 0, 100, 70)], category="Frame"),
fr("frame-1", "Frame 1", 23, "A noisy, flickering dark border around the picture.", EDGE + """
struct Params { noise: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = edge_distance(uv);
    let n = fbm(uv * 20.0 + vec2<f32>(floor(frame.time * 12.0) * 0.37));
    let edge = 0.04 + n * 0.05 * params.noise / 100.0;
    let m = smoothstep(edge, edge + 0.01, d);
    return vec4<f32>(c.rgb * m, c.a);
}
""", [p("noise", "Noise", 0, 100, 100)], category="Frame"),
fr("photo-frame", "Photo Frame", 24, "The picture as an instant photo with a white border, thicker at the bottom.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let side = 0.05;
    let bottom = 0.16;
    if (px.x < side || px.x > w - side || px.y < side || px.y > 1.0 - bottom) {
        let shade = 0.95 - 0.04 * (px.y);
        return vec4<f32>(vec3<f32>(shade, shade, shade * 0.97), 1.0);
    }
    let q = vec2<f32>((px.x - side) / (w - 2.0 * side), (px.y - side) / (1.0 - side - bottom));
    let c = sample(vec2<f32>(0.5) + (q - vec2<f32>(0.5)) * 0.95);
    return vec4<f32>(fade_print(c.rgb), c.a);
}

fn fade_print(rgb: vec3<f32>) -> vec3<f32> {
    return rgb * vec3<f32>(1.04, 1.0, 0.92) * 0.95 + vec3<f32>(0.02);
}
""", [], category="Frame"),
fr("white-border", "White Border", 25, "A white border that pulses gently around the picture.", EDGE + """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let w = params.size / 100.0 * 0.08 * (0.8 + 0.2 * sin(frame.time * rate() * 4.0));
    return select(c, vec4<f32>(1.0, 1.0, 1.0, 1.0), edge_distance(uv) < w);
}
""", [SPEED, p("size", "Size", 0, 100, 50)], category="Frame"),
fr("white-sprockets", "White Sprockets", 26, "White sprocket holes run along the top and bottom of the picture.", """
struct Params { texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let px = uv * frame.size / frame.size.y;
    let band = 0.07;
    let y = select(px.y, 1.0 - px.y, px.y > 0.5);
    if (y < band) {
        let hole = abs(y - band * 0.5) < band * 0.25 && abs(fract(px.x * 8.0) - 0.5) < 0.2;
        let k = params.texture / 100.0;
        return select(vec4<f32>(c.rgb * (1.0 - 0.9 * k), c.a), vec4<f32>(1.0, 1.0, 1.0, 1.0), hole);
    }
    return c;
}
""", [p("texture", "Strength", 0, 100, 100)], category="Frame"),
fr("rgb-border", "RGB Border", 27, "Red, green and blue borders shift around the picture.", EDGE + """
struct Params { speed: f32, shift: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate() * 2.0;
    let k = params.shift / 100.0 * 0.02;
    let r = sample(uv + vec2<f32>(sin(t), cos(t)) * k);
    let g = sample(uv);
    let b = sample(uv - vec2<f32>(sin(t), cos(t)) * k);
    let d = edge_distance(uv);
    let rim = smoothstep(0.03, 0.0, d);
    let rgb = vec3<f32>(r.r, g.g, b.b) + rainbow(fract(uv.x + uv.y + t * 0.2)) * rim;
    return vec4<f32>(rgb, g.a);
}
""", [p("speed", "Speed", 0, 100, 67), p("shift", "Shift", 0, 100, 100)], category="Frame"),
fr("electro-border", "Electro Border", 28, "Crackling electric light runs around the edge of the picture.", EDGE + """
struct Params { speed: f32, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = edge_distance(uv);
    let t = frame.time * rate() * 3.0;
    let n = fbm(uv * 12.0 + vec2<f32>(t, -t));
    let w = params.size / 100.0 * 0.05;
    let bolt = exp(-abs(d - w * n * 1.5) / 0.004) * params.strength / 100.0;
    let glow = exp(-d / (w + 0.01)) * 0.4 * params.strength / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(0.4, 0.7, 1.6) * (bolt * 2.0 + glow), c.a);
}
""", [p("speed", "Speed", 0, 100, 50), p("size", "Size", 0, 100, 60), p("strength", "Strength", 0, 100, 50)], category="Frame", intensity="strength"),
fr("flashing-frame", "Flashing Frame", 29, "A bright frame flashes around the picture on the beat.", EDGE + """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate());
    let on = exp(-ph * 5.0);
    let rim = smoothstep(0.05, 0.0, edge_distance(uv)) * on;
    return vec4<f32>(c.rgb + rainbow(floor(frame.time * rate()) * 0.31) * rim * 2.0, c.a);
}
""", [p("speed", "Speed", 0, 100, 80)], category="Frame"),
fr("flame-frame", "Flame Frame", 30, "Flames burn all around the edge of the picture.", EDGE + """
struct Params { speed: f32, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = edge_distance(uv);
    let t = frame.time * (0.5 + rate());
    let n = fbm(vec2<f32>(uv.x * 8.0, uv.y * 8.0 - t * 2.0));
    let w = params.size / 100.0 * 0.15;
    let flame = smoothstep(w, 0.0, d - n * w * 0.8) * params.strength / 100.0;
    let tint = mix(vec3<f32>(3.0, 1.0, 0.1), vec3<f32>(1.2, 0.2, 0.02), smoothstep(0.0, w, d));
    return vec4<f32>(mix(c.rgb, tint, clamp(flame, 0.0, 1.0)), c.a);
}
""", [p("speed", "Speed", 0, 100, 40), p("size", "Size", 0, 100, 60), p("strength", "Strength", 0, 100, 60)], category="Frame", intensity="strength"),
fr("fire-edges", "Fire Edges", 31, "Fire rises from the bottom edge of the picture.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.5 + rate());
    let n = fbm(vec2<f32>(uv.x * 6.0, uv.y * 4.0 + t * 2.0));
    let h = (1.0 - uv.y) * 2.5 - n * 1.2;
    let flame = smoothstep(0.6, 0.0, h);
    let tint = mix(vec3<f32>(1.2, 0.15, 0.02), vec3<f32>(3.0, 1.6, 0.4), smoothstep(0.2, 0.0, h));
    return vec4<f32>(mix(c.rgb, tint, flame), c.a);
}
""", [SPEED], category="Frame"),
fr("flames", "Flames", 32, "Flames roar up from below, lighting the picture.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.5 + rate());
    let n = fbm(vec2<f32>(uv.x * 5.0, uv.y * 3.0 + t * 2.5));
    let h = (1.0 - uv.y) * 1.6 - n;
    let flame = smoothstep(0.4, -0.2, h);
    let tint = mix(vec3<f32>(1.4, 0.2, 0.02), vec3<f32>(3.0, 1.8, 0.5), smoothstep(0.0, -0.3, h));
    let lit = c.rgb * (1.0 + 0.3 * (1.0 - uv.y)) * vec3<f32>(1.1, 0.95, 0.8);
    return vec4<f32>(mix(lit, tint, flame), c.a);
}
""", [SPEED], category="Frame"),
fr("flames-2", "Flames 2", 33, "Blue-hot flames lick up the sides of the picture.", EDGE + """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.5 + rate());
    let side = min(uv.x, 1.0 - uv.x) * frame.size.x / frame.size.y;
    let n = fbm(vec2<f32>(side * 6.0, uv.y * 4.0 + t * 2.0));
    let h = side * 6.0 - n * 1.5 + (1.0 - uv.y) * -0.5;
    let flame = smoothstep(0.8, 0.0, h);
    let tint = mix(vec3<f32>(0.1, 0.3, 1.5), vec3<f32>(1.0, 1.4, 3.0), smoothstep(0.4, 0.0, h));
    return vec4<f32>(mix(c.rgb, tint, flame), c.a);
}
""", [SPEED], category="Frame"),
fr("fire", "Fire", 34, "A wall of fire burns up through the lower picture.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.5 + rate());
    let n = fbm(vec2<f32>(uv.x * 4.0, uv.y * 2.5 + t * 3.0)) * 0.7 + fbm(vec2<f32>(uv.x * 9.0, uv.y * 6.0 + t * 4.0)) * 0.3;
    let h = (1.0 - uv.y) * 1.2 - n * 0.9;
    let flame = smoothstep(0.35, -0.05, h);
    let tint = mix(vec3<f32>(1.2, 0.18, 0.02), vec3<f32>(3.2, 1.9, 0.6), smoothstep(0.1, -0.2, h));
    return vec4<f32>(mix(c.rgb, tint, flame * 0.9), c.a);
}
""", [SPEED], category="Frame"),
fr("cartoon-border", "Cartoon Border", 35, "A wobbly, hand-drawn cartoon outline frames the picture.", EDGE + """
struct Params { speed: f32, blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = floor(frame.time * (2.0 + rate() * 6.0));
    let n = vnoise(uv * 15.0 + vec2<f32>(t * 3.1)) - 0.5;
    let d = edge_distance(uv) + n * 0.01;
    let w = 0.05;
    let ink = smoothstep(w + 0.006, w, d) * smoothstep(w - 0.012, w - 0.006, d);
    let outside = step(d, w - 0.006);
    let paper = vec3<f32>(1.0, 0.85, 0.2);
    var rgb = select(c.rgb, paper, outside > 0.5);
    rgb = mix(rgb, vec3<f32>(0.02), ink);
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("blur", "Wobble", 0, 100, 50)], category="Frame"),
fr("insta", "Insta", 36, "A square photo post: the picture cropped square on a white card.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let half = 0.38;
    if (abs(px.x) > half || abs(px.y + 0.03) > half) {
        let card = abs(px.x) < half + 0.04 && abs(px.y + 0.0) < half + 0.1;
        return select(vec4<f32>(0.9, 0.9, 0.92, 1.0), vec4<f32>(1.0, 1.0, 1.0, 1.0), card);
    }
    let q = vec2<f32>(0.5) + vec2<f32>(px.x, px.y + 0.03) / (2.0 * half) * vec2<f32>(frame.size.y / frame.size.x, 1.0);
    return sample(q);
}
""", [], category="Frame"),
fr("torn-frames", "Torn Frames", 37, "The picture torn into ragged paper pieces that jostle.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (1.0 + rate() * 4.0));
    let n = fbm(vec2<f32>(uv.y * 8.0, t));
    let tear = abs(uv.x - 0.5 - (n - 0.5) * 0.15);
    let side = select(-1.0, 1.0, uv.x > 0.5 + (n - 0.5) * 0.15);
    let off = vec2<f32>(side * 0.01, (hash(vec2<f32>(side, t), 1.0) - 0.5) * 0.02);
    let c = sample(uv - off);
    let paper = smoothstep(0.012, 0.004, tear);
    return vec4<f32>(mix(c.rgb, vec3<f32>(0.95, 0.93, 0.88), paper), c.a);
}
""", [SPEED], category="Frame"),
fr("electro-heart", "Electro Heart", 38, "A crackling electric heart pulses around the middle of the picture.", """
struct Params { speed: f32, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let t = frame.time * rate() * 3.0;
    let s = mix(0.4, 1.0, params.size / 100.0) * (1.0 + 0.05 * sin(t * 2.0));
    let n = fbm(d * 10.0 + vec2<f32>(t)) - 0.5;
    let sd = heart_sdf(vec2<f32>(d.x, -d.y) / s * 1.4) + n * 0.08;
    let bolt = exp(-abs(sd) / 0.012) * params.strength / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(1.6, 0.3, 0.9) * bolt * 1.5, c.a);
}
""", [p("speed", "Speed", 0, 100, 42), p("size", "Size", 0, 100, 100), p("strength", "Strength", 0, 100, 47)], category="Love", intensity="strength"),
fr("neon-frame", "Neon", 39, "A glowing neon tube frames the picture, its colour slowly turning.", EDGE + """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = edge_distance(uv);
    let tube = exp(-pow((d - 0.06) / 0.006, 2.0));
    let glow = exp(-abs(d - 0.06) / 0.03) * 0.5;
    let tint = rainbow(fract(frame.time * 0.1));
    let k = params.strength / 100.0;
    return vec4<f32>(c.rgb * (1.0 - 0.3 * k) + tint * (tube * 2.0 + glow) * k, c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], category="Party", shelves=["Party & Club"], intensity="strength"),
]
