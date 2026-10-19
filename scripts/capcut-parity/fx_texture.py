from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

def tx(slug, name, order, desc, body, params, category="Texture", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + NOISE + RAINBOW + HEART + GLINT + body, params, **kw)

def folds(seed, creases, angle):
    return """
struct Params { texture: f32 }

// Paper folded and opened out: the light catches each crease, one side of
// it lit and the other in shade, and the paper's grain shows through.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y);
    var shade = 0.0;
    for (var i = 0; i < CREASES; i++) {
        let fi = f32(i);
        let a = ANGLE + hash(vec2<f32>(fi, SEED), 1.0) * 3.14159265;
        let n = vec2<f32>(cos(a), sin(a));
        let off = (hash(vec2<f32>(fi, SEED), 2.0) - 0.5) * aspect;
        let d = dot(q - vec2<f32>(aspect * 0.5, 0.5), n) - off * 0.6;
        shade += sign(d) * exp(-abs(d) / 0.04) * 0.5 - exp(-abs(d) / 0.004) * 0.6;
    }
    let grain = (fbm(uv * 60.0) - 0.5) * 0.15;
    let k = params.texture / 100.0;
    let light = 1.0 + (shade * 0.25 + grain) * k;
    let paper = mix(c.rgb, c.rgb * vec3<f32>(1.02, 1.0, 0.95), k * 0.5);
    return vec4<f32>(paper * light, c.a);
}
""".replace("CREASES", str(creases)).replace("SEED", f"{float(seed)}").replace("ANGLE", f"{float(angle)}")

TEX = [p("texture", "Strength", 0, 100, 100)]

PACKAGES = [
tx("folds", "Folds", 10, "The picture printed on paper that has been folded and opened out.", folds(1, 2, 0.0), TEX, intensity="texture"),
tx("folds-2", "Folds 2", 11, "Paper creased many times over, the picture printed on it.", folds(2, 5, 0.3), TEX, intensity="texture"),
tx("folds-4", "Folds 4", 12, "A picture on paper folded into quarters.", folds(4, 2, 1.5707963), TEX, intensity="texture"),
tx("folds-5", "Folds 5", 13, "Crumpled paper smoothed out under the picture.", folds(5, 8, 0.7), TEX, intensity="texture"),
tx("paper-tear", "Paper Tear", 14, "A ragged tear runs across the picture, white paper showing at its edge.", """
struct Params { texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let edge = 0.5 + (fbm(vec2<f32>(uv.x * 8.0, 1.0)) - 0.5) * 0.25 + (vnoise(vec2<f32>(uv.x * 60.0, 2.0)) - 0.5) * 0.02;
    let d = uv.y - edge;
    let k = params.texture / 100.0;
    let paper = smoothstep(0.02, 0.008, abs(d)) * k;
    let shadow = select(1.0, 1.0 - exp(-d / 0.02) * 0.4 * k, d > 0.0);
    let shifted = select(c, sample(uv + vec2<f32>(0.0, 0.01 * k)), d > 0.0);
    return vec4<f32>(mix(shifted.rgb * shadow, vec3<f32>(0.96, 0.95, 0.9), paper), c.a);
}
""", TEX, intensity="texture"),
tx("grain", "Grain", 15, "Fine film grain over the picture.", """
struct Params { texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = hash(floor(uv * frame.size), fract(frame.time * 7.31)) - 0.5;
    return vec4<f32>(c.rgb * (1.0 + n * 0.25 * params.texture / 100.0), c.a);
}
""", TEX, intensity="texture"),
tx("old", "Old", 16, "An old, yellowed photograph: faded, stained and spotted.", """
struct Params { texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.texture / 100.0;
    let l = luma(c.rgb);
    let aged = mix(c.rgb, vec3<f32>(l * 1.08, l * 0.9, l * 0.62), 0.7) * 0.92 + vec3<f32>(0.04, 0.03, 0.0);
    let stain = smoothstep(0.55, 0.8, fbm(uv * 3.0)) * 0.25;
    let spots = step(0.996, hash(floor(uv * frame.size / 4.0), 3.0)) * 0.5;
    let vig = 1.0 - smoothstep(0.3, 0.9, length(uv - vec2<f32>(0.5)) * 1.2) * 0.5;
    let rgb = (aged * (1.0 - stain * vec3<f32>(0.2, 0.5, 0.9)) + vec3<f32>(spots)) * vig;
    return vec4<f32>(mix(c.rgb, rgb, k), c.a);
}
""", TEX, intensity="texture"),
tx("dot-silkscreen", "Dot Silkscreen", 17, "The picture screen-printed in coloured halftone dots.", """
struct Params { size: f32, color: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let cell = mix(4.0, 18.0, params.size / 100.0);
    let a = 0.7853982;
    let px = uv * frame.size;
    let r = vec2<f32>(px.x * cos(a) - px.y * sin(a), px.x * sin(a) + px.y * cos(a)) / cell;
    let local = fract(r) - vec2<f32>(0.5);
    let l = clamp(to_display(vec3<f32>(luma(c.rgb))).x, 0.0, 1.0);
    let dot_size = sqrt(1.0 - l) * 0.7;
    let ink = smoothstep(dot_size, dot_size - 0.08, length(local));
    let inkc = mix(vec3<f32>(0.05, 0.05, 0.1), c.rgb * 0.5, params.color / 100.0);
    let paper = mix(vec3<f32>(0.95, 0.93, 0.85), c.rgb * 1.1 + vec3<f32>(0.1), params.color / 100.0 * 0.5);
    return vec4<f32>(mix(paper, inkc, ink), c.a);
}
""", [p("size", "Dot size", 0, 100, 50), p("color", "Colour", 0, 100, 50)], category="Stylize"),
tx("blue-mosaic", "Blue Mosaic", 18, "The picture laid in blue glass tiles.", """
struct Params { size: f32, texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = mix(6.0, 30.0, params.size / 100.0);
    let cells = frame.size / px;
    let cell = floor(uv * cells);
    let c = sample((cell + vec2<f32>(0.5)) / cells);
    let local = fract(uv * cells);
    let grout = step(0.08, local.x) * step(0.08, local.y);
    let l = luma(c.rgb);
    let tile = mix(c.rgb, vec3<f32>(l * 0.4, l * 0.75, l * 1.4), params.texture / 100.0) * (0.85 + 0.3 * hash(cell, 1.0));
    return vec4<f32>(tile * mix(0.3, 1.0, grout), c.a);
}
""", [p("size", "Tile size", 0, 100, 70), p("texture", "Blue", 0, 100, 50)], category="Stylize"),
tx("energy", "Energy", 19, "Arcs of energy crackle across the picture.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    var light = 0.0;
    for (var i = 0; i < 3; i++) {
        let fi = f32(i);
        let t = frame.time * (1.5 + fi * 0.3);
        let y = 0.5 + (fbm(vec2<f32>(uv.x * 3.0 + fi * 10.0, floor(t * 6.0))) - 0.5) * 0.8;
        light += 0.003 / (abs(uv.y - y) + 0.003);
    }
    return vec4<f32>(c.rgb + vec3<f32>(0.4, 0.7, 1.6) * light * 0.6, c.a);
}
""", [], category="Light"),
tx("circuit", "Circuit", 20, "Glowing circuit traces light up across the picture.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let cells = vec2<f32>(16.0, 16.0 * frame.size.y / frame.size.x);
    let q = uv * cells;
    let cell = floor(q);
    let f = fract(q);
    let h = hash(cell, 1.0);
    // A trace through each cell: straight, turning, or a pad.
    var d: f32;
    if (h < 0.4) {
        d = abs(f.y - 0.5);
    } else if (h < 0.8) {
        d = abs(f.x - 0.5);
    } else {
        d = abs(length(f - vec2<f32>(0.5)) - 0.25);
    }
    let trace = smoothstep(0.08, 0.02, d);
    let pulse = 0.5 + 0.5 * sin(frame.time * 3.0 - (cell.x + cell.y) * 0.5);
    return vec4<f32>(c.rgb * 0.7 + vec3<f32>(0.1, 1.0, 0.6) * trace * pulse * 0.8, c.a);
}
""", [], category="Stylize"),
tx("warning", "Warning", 21, "Flashing red alarm light and hazard stripes at the edges.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let alarm = 0.5 + 0.5 * sin(frame.time * 8.0);
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let d = min(min(px.x, w - px.x), min(px.y, 1.0 - px.y));
    let stripe = step(0.5, fract((px.x + px.y) * 8.0 - frame.time));
    let band = step(d, 0.04);
    let hazard = select(vec3<f32>(0.05), vec3<f32>(1.0, 0.8, 0.05), stripe > 0.5);
    let red = c.rgb * mix(vec3<f32>(1.0), vec3<f32>(1.4, 0.5, 0.5), alarm);
    return vec4<f32>(mix(red, hazard, band), c.a);
}
""", [], category="Fun"),
tx("question-marks", "Question Marks", 22, "Question marks pop up around a puzzled picture.", """
fn mark(p: vec2<f32>) -> f32 {
    // A question mark drawn from an arc, a stem and a dot.
    let arc = abs(length(p - vec2<f32>(0.0, -0.3)) - 0.3) < 0.09 && (p.y < -0.3 || p.x > 0.0);
    let stem = abs(p.x) < 0.09 && p.y > -0.05 && p.y < 0.25;
    let dot = length(p - vec2<f32>(0.0, 0.48)) < 0.1;
    return select(0.0, 1.0, arc || stem || dot);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let cells = vec2<f32>(5.0, 5.0 * frame.size.y / frame.size.x);
    let q = uv * cells;
    let cell = floor(q);
    let born = hash(cell, 1.0) * 2.0;
    let t = fract((frame.time - born) * 0.5);
    let show = step(0.65, hash(cell, 2.0)) * smoothstep(0.0, 0.1, t) * smoothstep(0.6, 0.4, t);
    let s = 0.35 + 0.1 * sin(t * 12.0);
    let m = mark((fract(q) - vec2<f32>(0.5)) / s * 0.5) * show;
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0, 0.85, 0.1), m), c.a);
}
""", [], category="Fun"),
tx("quick-math", "Quick Math", 23, "Equations and symbols swirl over a thinking face, a meme classic.", """
fn glyph(p: vec2<f32>, kind: f32) -> f32 {
    let a = abs(p);
    if (kind < 0.25) {
        return select(0.0, 1.0, (a.x < 0.4 && a.y < 0.08) || (a.y < 0.4 && a.x < 0.08));
    }
    if (kind < 0.5) {
        return select(0.0, 1.0, abs(a.y - 0.15) < 0.07 && a.x < 0.4);
    }
    if (kind < 0.75) {
        let d = abs(p.x + p.y) * 0.707;
        let e = abs(p.x - p.y) * 0.707;
        return select(0.0, 1.0, (d < 0.07 || e < 0.07) && length(p) < 0.45);
    }
    return select(0.0, 1.0, abs(length(p) - 0.3) < 0.07);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let a = atan2(d.y, d.x) + frame.time * 0.4;
    let r = length(d);
    let q = vec2<f32>(a * 2.0, r * 6.0);
    let cell = floor(q);
    let show = step(0.5, hash(cell, 1.0)) * smoothstep(0.1, 0.3, r);
    let g = glyph((fract(q) - vec2<f32>(0.5)) * 2.0, hash(cell, 2.0)) * show;
    let blue = mix(c.rgb, c.rgb * vec3<f32>(0.85, 0.95, 1.1), 0.5);
    return vec4<f32>(mix(blue, vec3<f32>(1.0), g * 0.9), c.a);
}
""", [], category="Fun"),
tx("super-like", "Super Like", 24, "A big heart pops up and beats over the picture.", """
struct Params { speed: f32, size: f32, shift: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate() * 0.5);
    let pop = smoothstep(0.0, 0.15, ph) * (1.0 + 0.2 * exp(-ph * 8.0) * sin(ph * 40.0));
    let centre = vec2<f32>(0.5, 0.5 - params.shift / 100.0 * 0.3);
    let d = (uv - centre) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let s = mix(0.15, 0.6, params.size / 100.0) * pop;
    let sd = heart_sdf(vec2<f32>(d.x, -d.y) / max(s, 1e-3));
    let m = smoothstep(0.03, -0.03, sd);
    let shine = exp(-length(d / max(s, 1e-3) - vec2<f32>(-0.2, -0.25)) * 8.0) * m;
    let heart = vec3<f32>(1.0, 0.1, 0.3) + vec3<f32>(shine);
    return vec4<f32>(mix(c.rgb, heart, m), c.a);
}
""", [p("speed", "Speed", 0, 100, 50), p("size", "Size", 0, 100, 20), p("shift", "Height", 0, 100, 0)], category="Love"),
tx("oh-my-god", "Oh My God", 25, "Shock: the picture zooms in hard with speed lines and a red flash.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * 0.5);
    let z = 1.0 + 0.25 * smoothstep(0.0, 0.1, ph);
    let c = sample(moved(uv, vec2<f32>(0.0), 0.0, z));
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let a = atan2(d.y, d.x);
    let lines = step(0.85, hash(vec2<f32>(floor(a * 40.0), floor(frame.time * 12.0)), 1.0)) * smoothstep(0.25, 0.6, length(d));
    let flash = exp(-ph * 10.0) * 0.4;
    let rgb = mix(c.rgb, vec3<f32>(1.0), lines * 0.8) * (1.0 + vec3<f32>(flash, -flash * 0.5, -flash * 0.5));
    return vec4<f32>(rgb, c.a);
}
""", [], category="Fun"),
tx("splice", "Splice", 26, "The picture cut into strips and spliced back slightly out of line.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let n = 6.0;
    let strip = floor(uv.x * n);
    let t = floor(frame.time * 2.0);
    let off = (hash(vec2<f32>(strip, t), 1.0) - 0.5) * 0.06;
    let c = sample(vec2<f32>(uv.x, fract(uv.y + off)));
    let seam = smoothstep(0.01, 0.0, abs(fract(uv.x * n) - 0.0)) + smoothstep(0.99, 1.0, fract(uv.x * n));
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0), seam * 0.8), c.a);
}
""", [], category="Fun"),
tx("graphic-3", "Graphic 3", 27, "Bold graphic shapes slide and spin over the corners of the picture.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time;
    let px = uv * frame.size / frame.size.y;
    let w = frame.size.x / frame.size.y;
    let ring = abs(length(px - vec2<f32>(0.15, 0.15) - vec2<f32>(sin(t), cos(t)) * 0.02) - 0.1) < 0.012;
    let tri_p = px - vec2<f32>(w - 0.18, 0.82);
    let a = t * 0.8;
    let rp = vec2<f32>(tri_p.x * cos(a) - tri_p.y * sin(a), tri_p.x * sin(a) + tri_p.y * cos(a));
    let tri = rp.y < 0.06 && rp.y > -0.08 + abs(rp.x) * 1.7 - 0.0;
    let bars = px.y > 0.9 && px.x < 0.45 && fract(px.x * 10.0 - t) < 0.5;
    var rgb = c.rgb;
    rgb = select(rgb, vec3<f32>(1.0), ring);
    rgb = select(rgb, vec3<f32>(1.0, 0.85, 0.1), tri);
    rgb = select(rgb, vec3<f32>(0.1, 0.8, 1.0), bars);
    return vec4<f32>(rgb, c.a);
}
""", [], category="Fun"),
tx("lightning-crack", "Lightning Crack", 28, "Lightning cracks across the picture, lighting it in flashes.", """
struct Params { speed: f32, distortion: f32 }

fn bolt(uv: vec2<f32>, seed: f32) -> f32 {
    let x = 0.5 + (fbm(vec2<f32>(uv.y * 3.0, seed)) - 0.5) * 0.7 + (vnoise(vec2<f32>(uv.y * 40.0, seed)) - 0.5) * 0.05;
    return 0.002 / (abs(uv.x - x) * frame.size.x / frame.size.y + 0.002);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * (0.5 + rate());
    let n = floor(t);
    let on = exp(-fract(t) * 6.0) * step(0.4, hash(vec2<f32>(n, 0.0), 1.0));
    let shake = (hash(vec2<f32>(floor(t * 20.0), 1.0), 2.0) - 0.5) * 0.01 * on * params.distortion / 100.0;
    let c = sample(uv + vec2<f32>(shake, 0.0));
    let b = bolt(uv, n) * on;
    return vec4<f32>(c.rgb * (0.6 + on * 0.8) + vec3<f32>(0.7, 0.8, 1.2) * b * 3.0, c.a);
}
""", [p("speed", "Speed", 0, 100, 80), p("distortion", "Shake", 0, 100, 50)], category="Light"),
tx("lightning-fx", "Lightning", 29, "Forks of lightning flash across a stormy, darkened sky.", """
struct Params { speed: f32, luminance: f32 }

fn fork(uv: vec2<f32>, seed: f32, x0: f32) -> f32 {
    let x = x0 + (fbm(vec2<f32>(uv.y * 4.0, seed)) - 0.5) * 0.5;
    return 0.0015 / (abs(uv.x - x) * frame.size.x / frame.size.y + 0.0015) * smoothstep(0.9, 0.0, uv.y * hash(vec2<f32>(seed, 3.0), 1.0) * 1.2);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * (0.5 + rate());
    let n = floor(t);
    let on = exp(-fract(t) * 5.0) * step(0.3, hash(vec2<f32>(n, 0.0), 1.0));
    let c = sample(uv);
    let storm = c.rgb * vec3<f32>(0.6, 0.65, 0.85);
    let b = fork(uv, n, 0.3 + hash(vec2<f32>(n, 1.0), 1.0) * 0.4) * on;
    let k = params.luminance / 100.0;
    return vec4<f32>(storm * (1.0 + on * k) + vec3<f32>(0.8, 0.85, 1.3) * b * 3.0, c.a);
}
""", [p("speed", "Speed", 0, 100, 40), p("luminance", "Flash", 0, 100, 40)], category="Light"),
tx("wipe-board", "Wipe Board", 30, "A wiper sweeps back and forth across the picture, clearing a fog it leaves behind.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let pos = 0.5 + 0.5 * sin(frame.time * rate() * 2.0);
    let fog = smoothstep(0.0, 0.4, abs(uv.x - pos));
    let soft = soften(uv, 6.0);
    let rgb = mix(c.rgb, soft * 0.9 + vec3<f32>(0.12), fog * 0.7);
    let blade = smoothstep(0.01, 0.0, abs(uv.x - pos));
    return vec4<f32>(mix(rgb, vec3<f32>(0.05), blade), c.a);
}
""", [SPEED], category="Fun"),
tx("astral", "Astral", 31, "The picture drifts in a starry astral haze, a faint double floating off it.", """
struct Params { speed: f32, range: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * rate();
    let ghost = sample(moved(uv, vec2<f32>(sin(t) * 0.02, -0.02 - 0.01 * cos(t)), 0.0, 1.05));
    let k = params.range / 100.0;
    let cells = vec2<f32>(20.0, 20.0 * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let star = glint(fract(uv * cells) - vec2<f32>(0.5), 0.5) * step(0.93, hash(cell, 1.0)) * (0.5 + 0.5 * sin(t * 4.0 + hash(cell, 2.0) * 6.28));
    let rgb = c.rgb * (1.0 - 0.25 * k) + ghost.rgb * vec3<f32>(0.5, 0.6, 1.0) * 0.4 * k + vec3<f32>(star) * k;
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("range", "Strength", 0, 100, 100)], category="Light", intensity="range"),
tx("explosion", "Explosion", 32, "A burst of fire explodes out from the centre with a white flash.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate() * 0.4);
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let r = length(d);
    let a = atan2(d.y, d.x);
    let n = fbm(vec2<f32>(a * 3.0, r * 4.0 - ph * 6.0));
    let front = ph * 1.3;
    let fire = smoothstep(front, front - 0.3, r + n * 0.2) * (1.0 - ph);
    let flash = exp(-ph * 12.0);
    let tint = mix(vec3<f32>(3.0, 1.6, 0.5), vec3<f32>(1.0, 0.25, 0.05), smoothstep(0.0, front, r));
    let rgb = mix(c.rgb, tint, clamp(fire, 0.0, 1.0)) + vec3<f32>(flash);
    return vec4<f32>(rgb, c.a);
}
""", [SPEED], category="Light"),
tx("fireworks-2", "Fireworks 2", 33, "Fireworks burst in bright showers of sparks over a darkened sky.", """
struct Params { speed: f32 }

fn burst(uv: vec2<f32>, id: f32, t: f32) -> vec3<f32> {
    let life = fract(t + hash(vec2<f32>(id, 0.0), 1.0));
    let round = floor(t + hash(vec2<f32>(id, 0.0), 1.0));
    let centre = vec2<f32>(0.2 + 0.6 * hash(vec2<f32>(id, round), 2.0), 0.15 + 0.4 * hash(vec2<f32>(id, round), 3.0));
    let d = (uv - centre) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let r = length(d);
    let a = atan2(d.y, d.x);
    let spoke = fract(a / 6.2831853 * 24.0);
    let reach = life * 0.3;
    let spark = smoothstep(0.08, 0.0, abs(spoke - 0.5) - 0.42) * exp(-abs(r - reach) / 0.01) * (1.0 - life);
    let colour = rainbow(hash(vec2<f32>(id, round), 4.0));
    return colour * spark * 3.0 + vec3<f32>(exp(-r / 0.03) * exp(-life * 10.0));
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.3 + rate() * 0.5);
    var light = vec3<f32>(0.0);
    for (var i = 0; i < 4; i++) {
        light += burst(uv, f32(i), t + f32(i) * 0.37);
    }
    return vec4<f32>(c.rgb * 0.7 + light, c.a);
}
""", [SPEED], category="Party", shelves=["Party & Club"]),
tx("collision-sparks", "Collision Sparks", 34, "Sparks fly from a grinding collision at the bottom of the frame.", """
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    var light = 0.0;
    let origin = vec2<f32>(0.5, 0.95);
    for (var i = 0; i < 24; i++) {
        let fi = f32(i);
        let born = hash(vec2<f32>(fi, 0.0), 1.0);
        let life = fract(frame.time * 1.5 + born);
        let round = floor(frame.time * 1.5 + born);
        let a = -1.5707963 + (hash(vec2<f32>(fi, round), 2.0) - 0.5) * 2.4;
        let v = vec2<f32>(cos(a), sin(a)) * (0.4 + 0.6 * hash(vec2<f32>(fi, round), 3.0));
        let pos = origin + v * life * 0.6 + vec2<f32>(0.0, 0.5) * life * life;
        let d = (uv - pos) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
        let along = normalize(v + vec2<f32>(0.0, life));
        let streak = exp(-pow(dot(d, vec2<f32>(-along.y, along.x)) / 0.002, 2.0)) * smoothstep(0.03, 0.0, abs(dot(d, along)));
        light += streak * (1.0 - life);
    }
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.6, 0.2) * light * 3.0, c.a);
}
""", [], category="Light"),
]
