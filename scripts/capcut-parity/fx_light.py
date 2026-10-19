from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

def lt(slug, name, order, desc, body, params, category="Light", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + NOISE + RAINBOW + HUE + GLINT + body, params, **kw)

LEAK = """
struct Params { speed: f32, strength: f32 }

// Warm light spilling in from the edge of the frame, drifting.
fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * rate() * 0.3;
    let at = vec2<f32>(SOURCE) + vec2<f32>(sin(t), cos(t * 0.7)) * 0.15;
    let d = length((uv - at) * vec2<f32>(frame.size.x / frame.size.y, 1.0));
    let n = fbm(uv * 2.0 + vec2<f32>(t, -t * 0.5));
    let leak = exp(-d * d * 3.0) * (0.6 + 0.6 * n) * params.strength / 100.0;
    let tint = TINT;
    return vec4<f32>(c.rgb + tint * leak * 1.5, c.a);
}
"""

FOG = """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * rate() * 0.15;
    let n = fbm(uv * vec2<f32>(2.0, 3.0) + vec2<f32>(t, t * 0.3));
    let k = params.strength / 100.0 * smoothstep(0.3, 0.9, n);
    let tint = TINT;
    return vec4<f32>(mix(c.rgb, tint, k * 0.7) + tint * 0.05 * params.strength / 100.0, c.a);
}
"""

PACKAGES = [
lt("leak-1", "Leak 1", 10, "A warm orange light leak drifts across the corner of the frame.",
   LEAK.replace("SOURCE", "0.05, 0.15").replace("TINT", "vec3<f32>(1.0, 0.45, 0.12)"), [SPEED, p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("leak-2", "Leak 2", 11, "A pink-red light leak glows in from the side of the frame.",
   LEAK.replace("SOURCE", "0.95, 0.6").replace("TINT", "vec3<f32>(1.0, 0.2, 0.3)"), [SPEED, p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("light-leak-overlay", "Light leak", 12, "Streaks of warm film light leak across the picture.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * 0.2;
    let band = fbm(vec2<f32>(uv.x * 1.5 + t, uv.y * 0.3));
    let streak = smoothstep(0.35, 0.75, band) * smoothstep(1.2, 0.0, uv.y + 0.3 * sin(t));
    let tint = mix(vec3<f32>(1.0, 0.3, 0.05), vec3<f32>(1.0, 0.8, 0.4), band);
    return vec4<f32>(c.rgb + tint * streak * 1.6 * params.strength / 100.0, c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], intensity="strength"),
lt("sun", "Sun", 13, "Sunlight flares in from the top corner with a soft halo.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let aspect = frame.size.x / frame.size.y;
    let src = vec2<f32>(0.85, 0.1) + vec2<f32>(sin(frame.time * rate() * 0.5), 0.0) * 0.03;
    let d = (uv - src) * vec2<f32>(aspect, 1.0);
    let r = length(d);
    let k = params.strength / 100.0;
    let glow = exp(-r * 3.0) * 1.2 + exp(-r * 12.0) * 2.0;
    let rays = pow(max(0.0, sin(atan2(d.y, d.x) * 12.0 + frame.time * 0.3)), 8.0) * exp(-r * 2.0) * 0.4;
    // Ghosts of the lens along the line through the centre.
    let axis = (vec2<f32>(0.5) - src) * vec2<f32>(aspect, 1.0);
    var ghosts = 0.0;
    for (var i = 1; i <= 3; i++) {
        let g = src * vec2<f32>(aspect, 1.0) + axis * (0.6 * f32(i));
        ghosts += exp(-length(uv * vec2<f32>(aspect, 1.0) - g) * 30.0 / f32(i)) * 0.3;
    }
    let light = vec3<f32>(1.0, 0.85, 0.6) * (glow + rays) + vec3<f32>(0.6, 0.8, 1.0) * ghosts;
    return vec4<f32>(c.rgb * (1.0 + 0.1 * k) + light * k, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("sunset-4", "Sunset 4", 14, "A golden-hour wash: warm light from above fading to rose at the bottom.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0 * (0.85 + 0.15 * sin(frame.time * rate()));
    let top = vec3<f32>(1.0, 0.65, 0.25);
    let bottom = vec3<f32>(0.9, 0.35, 0.45);
    let tint = mix(top, bottom, uv.y);
    let rgb = mix(c.rgb, c.rgb * tint * 1.4, k * 0.6) + top * exp(-uv.y * 4.0) * 0.3 * k;
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("halo", "Halo", 15, "A soft ring of light breathes around the middle of the picture.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let r = length((uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0));
    let radius = 0.38 + 0.04 * sin(frame.time * rate() * 2.0);
    let ring = exp(-pow((r - radius) / 0.08, 2.0)) * params.strength / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.95, 0.85) * ring * 0.8, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("halo-2", "Halo 2", 16, "Rings of iridescent light ripple outward from the centre.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let r = length((uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0));
    let rings = pow(0.5 + 0.5 * sin(r * 25.0 - frame.time * rate() * 4.0), 6.0) * exp(-r * 1.5);
    let tint = rainbow(fract(r * 2.0 - frame.time * 0.2));
    return vec4<f32>(c.rgb + tint * rings * 0.6 * params.strength / 100.0, c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("angel", "Angel", 17, "Heavenly light from above with a soft white glow.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let beams = pow(max(0.0, sin(uv.x * 18.0 + uv.y * 4.0 + frame.time * 0.4)), 6.0) * (1.0 - uv.y) * 0.4;
    let top = exp(-uv.y * 3.0) * 0.5;
    let soft = mix(c.rgb, vec3<f32>(luma(c.rgb)), 0.15);
    return vec4<f32>(soft * (1.0 + 0.1 * k) + vec3<f32>(1.0, 0.97, 0.9) * (beams + top) * k, c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], intensity="strength"),
lt("mist", "Mist", 18, "A drifting mist rolls slowly over the picture.", FOG.replace("TINT", "vec3<f32>(0.85, 0.88, 0.9)"), [SPEED, p("strength", "Strength", 0, 100, 70)], intensity="strength"),
lt("purple-mist", "Purple Mist", 19, "A violet mist drifts over the picture.", FOG.replace("TINT", "vec3<f32>(0.55, 0.35, 0.85)"), [SPEED, p("strength", "Strength", 0, 100, 70)], intensity="strength"),
lt("soft-rose", "Soft Rose", 20, "A rosy haze softly tints and drifts over the picture.", FOG.replace("TINT", "vec3<f32>(1.0, 0.6, 0.7)"), [SPEED, p("strength", "Strength", 0, 100, 60)], intensity="strength"),
lt("window-shade", "Window", 21, "The shadow of a window frame lies across the picture in warm light.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let q = vec2<f32>(uv.x + uv.y * 0.35 + sin(frame.time * 0.2) * 0.02, uv.y);
    let panes = step(0.08, fract(q.x * 2.2)) * step(0.08, fract(q.y * 2.0));
    let light = mix(0.45, 1.15, panes * smoothstep(0.0, 0.3, q.x) * smoothstep(1.4, 0.8, q.x));
    let k = params.strength / 100.0;
    let lit = c.rgb * mix(1.0, light, k) * mix(vec3<f32>(1.0), vec3<f32>(1.08, 1.0, 0.88), panes * k);
    return vec4<f32>(lit, c.a);
}
""", [p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("train-window", "Train Window", 22, "Light and shadow flicker past as through the window of a moving train.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let x = uv.x + frame.time * rate() * 0.8;
    let posts = smoothstep(0.0, 0.05, fract(x * 1.5)) * smoothstep(0.25, 0.2, fract(x * 1.5));
    let n = vnoise(vec2<f32>(x * 4.0, 0.0));
    let light = mix(1.1, 0.5, posts) * (0.9 + 0.2 * n);
    return vec4<f32>(c.rgb * mix(1.0, light, params.strength / 100.0), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 70)], intensity="strength"),
lt("blinds-shade", "Blinds", 23, "The striped shadow of window blinds falls across the picture.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let y = uv.y + uv.x * 0.25 + sin(frame.time * 0.3) * 0.01;
    let slat = smoothstep(0.35, 0.45, fract(y * 9.0)) * smoothstep(0.95, 0.85, fract(y * 9.0));
    let light = mix(0.45, 1.15, slat);
    return vec4<f32>(c.rgb * mix(1.0, light, params.strength / 100.0), c.a);
}
""", [p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("blinds-2", "Blinds 2", 24, "Vertical blind shadows sway across the picture.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let x = uv.x + sin(frame.time * 0.5 + uv.y * 2.0) * 0.01;
    let slat = smoothstep(0.3, 0.4, fract(x * 10.0)) * smoothstep(0.95, 0.85, fract(x * 10.0));
    return vec4<f32>(c.rgb * mix(1.0, mix(0.45, 1.15, slat), params.strength / 100.0), c.a);
}
""", [p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("gleam", "Gleam", 25, "A diagonal gleam of light sweeps across the bright parts of the picture.", """
struct Params { size: f32, luminance: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let pos = fract(frame.time * 0.4) * 1.8 - 0.4;
    let coord = uv.x + uv.y * 0.5;
    let w = mix(0.03, 0.2, params.size / 100.0);
    let band = exp(-pow((coord - pos) / w, 2.0));
    let lift = smoothstep(0.2, 0.8, luma(c.rgb));
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.98, 0.9) * band * (0.3 + lift) * params.luminance / 100.0 * 1.5, c.a);
}
""", [p("size", "Width", 0, 100, 50), p("luminance", "Brightness", 0, 100, 55)], intensity="luminance"),
lt("edge-glow", "Edge Glow", 26, "The edges in the picture glow with light.", """
struct Params { luminance: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let e = edge_at(uv);
    let tint = vec3<f32>(0.6, 0.85, 1.0);
    return vec4<f32>(c.rgb + tint * e * params.luminance / 100.0 * 2.0, c.a);
}
""", [p("luminance", "Glow", 0, 100, 25)], intensity="luminance"),
lt("neon-outline", "Neon Outline", 27, "Everything outlined in shifting neon over a darkened picture.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let e = smoothstep(0.1, 0.5, edge_at(uv));
    let tint = rainbow(fract(uv.x * 0.5 + uv.y * 0.5 + frame.time * 0.2));
    let k = params.strength / 100.0;
    return vec4<f32>(mix(c.rgb, c.rgb * 0.25, k) + tint * e * 1.8 * k, c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], intensity="strength", category="Party", shelves=["Party & Club"]),
lt("color-flame", "Color Flame", 28, "Coloured flames of light lick up from the picture's edges.", """
struct Params { strength: f32, color: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = fbm(vec2<f32>(uv.x * 4.0, uv.y * 3.0 + frame.time * 1.5));
    let flame = smoothstep(0.6, 1.0, n + (uv.y - 0.4) * 0.8) * params.strength / 100.0;
    let tint = mix(vec3<f32>(1.0, 0.4, 0.05), rainbow(fract(uv.x + frame.time * 0.1)), params.color / 100.0);
    return vec4<f32>(c.rgb + tint * flame * 2.0, c.a);
}
""", [p("strength", "Strength", 0, 100, 100), p("color", "Colour", 0, 100, 100)], intensity="strength"),
lt("luminance-fx", "Luminance", 29, "The light of the picture pulses brighter and glows.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0 * (0.6 + 0.4 * sin(frame.time * 2.0));
    let bright = max(c.rgb - vec3<f32>(0.4), vec3<f32>(0.0));
    return vec4<f32>(c.rgb * (1.0 + 0.3 * k) + bright * 1.5 * k, c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], intensity="strength"),
lt("develop", "Develop", 30, "The picture develops out of white like a photograph in the tray.", """
struct Params { speed: f32, soft: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = smoothstep(0.0, 1.0, opening());
    let pale = mix(vec3<f32>(1.0), vec3<f32>(luma(c.rgb)) * vec3<f32>(1.1, 1.0, 0.85), 0.3);
    let rgb = mix(pale, c.rgb, t);
    return vec4<f32>(mix(rgb, rgb + vec3<f32>(0.05), params.soft / 100.0 * (1.0 - t)), c.a);
}
""", [SPEED, p("soft", "Softness", 0, 100, 100)], card={"moment": 0.6}),
lt("ethereal", "Ethereal", 31, "A dreamy, glowing double of the picture slowly turns over it.", """
struct Params { size: f32, rotate: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let a = sin(frame.time * 0.5) * 0.08 * params.rotate / 100.0;
    let ghost = sample(moved(uv, vec2<f32>(0.0), a, 1.0 + params.size / 100.0 * 0.15));
    let rgb = c.rgb * 0.7 + ghost.rgb * 0.5 + vec3<f32>(0.05, 0.04, 0.08);
    return vec4<f32>(rgb, c.a);
}
""", [p("size", "Size", 0, 100, 100), p("rotate", "Turn", 0, 100, 100)]),
lt("glowburst", "Glowburst", 32, "Bursts of glowing light bloom out from the centre on a beat.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let ph = fract(frame.time * rate() * 0.5);
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let r = length(d);
    let a = atan2(d.y, d.x);
    let rays = pow(max(0.0, sin(a * 10.0 + ph * 3.0)), 4.0);
    let burst = exp(-r / (0.1 + ph * 0.6)) * (1.0 - ph) * (0.5 + rays);
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.85, 0.5) * burst * 1.5, c.a);
}
""", [SPEED]),
lt("rainbow-haze", "Rainbow Haze", 33, "A haze of rainbow light drifts over the picture.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = fbm(uv * 2.0 + vec2<f32>(frame.time * rate() * 0.1, 0.0));
    let tint = rainbow(fract(n * 1.5 + uv.x * 0.5 + frame.time * 0.1));
    return vec4<f32>(mix(c.rgb, screen_light(c.rgb, tint), params.strength / 100.0 * 0.6), c.a);
}

fn screen_light(base: vec3<f32>, over: vec3<f32>) -> vec3<f32> {
    let b = min(base, vec3<f32>(1.0));
    return vec3<f32>(1.0) - (vec3<f32>(1.0) - b) * (vec3<f32>(1.0) - over) + (base - b);
}
""", [p("speed", "Speed", 0, 100, 100), p("strength", "Strength", 0, 100, 100)], intensity="strength"),
lt("by-the-fireplace", "By the Fireplace", 34, "The warm, flickering glow of a fire, with embers drifting up.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.5 + rate());
    let flicker = 0.85 + 0.15 * vnoise(vec2<f32>(t * 3.0, 0.0));
    let k = params.strength / 100.0;
    let warm = c.rgb * mix(vec3<f32>(1.0), vec3<f32>(1.25, 0.95, 0.65) * flicker, k);
    let glow = exp(-(1.0 - uv.y) * 3.0) * vec3<f32>(1.0, 0.4, 0.1) * 0.5 * k * flicker;
    let cells = vec2<f32>(18.0, 10.0);
    let q = vec2<f32>(uv.x, uv.y + t * 0.1) * cells;
    let cell = floor(q);
    let ember = exp(-dot(fract(q) - vec2<f32>(0.5), fract(q) - vec2<f32>(0.5)) * 60.0) * step(0.85, hash(cell, 1.0));
    return vec4<f32>(warm + glow + vec3<f32>(1.0, 0.5, 0.1) * ember * k, c.a);
}
""", [p("speed", "Speed", 0, 100, 20), p("strength", "Strength", 0, 100, 60)], intensity="strength"),
lt("magic", "Magic", 35, "A spell of swirling sparkles and violet glow.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * rate();
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let a = atan2(d.y, d.x) + t * 0.5;
    let r = length(d);
    let q = vec2<f32>(a * 3.0, r * 12.0 - t);
    let cell = floor(q);
    let f = fract(q) - vec2<f32>(0.5);
    let star = glint(f, 0.6) * step(0.8, hash(cell, 2.0)) * (0.5 + 0.5 * sin(t * 6.0 + hash(cell, 3.0) * 6.28));
    let k = params.strength / 100.0;
    let tint = mix(c.rgb, c.rgb * vec3<f32>(0.9, 0.8, 1.2), k * 0.5);
    return vec4<f32>(tint + vec3<f32>(0.85, 0.7, 1.0) * star * k * 1.5, c.a);
}
""", [p("speed", "Speed", 0, 100, 34), p("strength", "Strength", 0, 100, 80)], intensity="strength"),
lt("camera-flash-pop", "Flash 2", 36, "Paparazzi flashes go off from different spots around the frame.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (2.0 + rate() * 3.0);
    let n = floor(t);
    let ph = fract(t);
    let at = vec2<f32>(hash(vec2<f32>(n, 1.0), 1.0), hash(vec2<f32>(n, 2.0), 1.0));
    let d = length((uv - at) * vec2<f32>(frame.size.x / frame.size.y, 1.0));
    let flash = exp(-ph * 10.0);
    let star = glint((uv - at) * vec2<f32>(frame.size.x / frame.size.y, 1.0), 0.3);
    return vec4<f32>(c.rgb * (1.0 + flash * 1.5 * exp(-d * 2.0)) + vec3<f32>(star * flash * 2.0), c.a);
}
""", [SPEED], card={"moment": 0.855}),
]
