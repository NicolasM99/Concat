from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

def cl(slug, name, order, desc, body, params, category="Color", **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + NOISE + RAINBOW + HUE + body, params, **kw)

PARTY = ["Party & Club"]

PACKAGES = [
cl("colorful", "Colorful", 10, "The picture's hues cycle round the colour wheel.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    return vec4<f32>(saturation(turn_hue(c.rgb, frame.time * rate() * 120.0), 1.3), c.a);
}
""", [SPEED], category="Party", shelves=PARTY),
cl("club-mood", "Club Mood", 11, "Coloured club lights wash over the picture in turn.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * rate();
    let a = rainbow(fract(t * 0.5));
    let b = rainbow(fract(t * 0.5 + 0.5));
    let side = smoothstep(0.2, 0.8, uv.x + sin(t) * 0.3);
    let light = mix(a, b, side);
    let l = luma(c.rgb);
    return vec4<f32>(c.rgb * 0.4 + light * l * 1.4, c.a);
}
""", [SPEED], category="Party", shelves=PARTY),
cl("disco", "Disco", 12, "Disco light: the picture flashes through saturated colours on the beat.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = floor(frame.time * (2.0 + rate() * 4.0));
    let light = rainbow(hash(vec2<f32>(t, 0.0), 1.0));
    return vec4<f32>(mix(c.rgb, light * luma(c.rgb) * 2.0, 0.6), c.a);
}
""", [SPEED], category="Party", shelves=PARTY),
cl("rainbow-neon", "Rainbow Neon", 13, "Bands of rainbow neon roll across the picture.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let band = rainbow(fract(uv.x * 0.8 - uv.y * 0.4 + frame.time * rate() * 0.3));
    let k = params.strength / 100.0;
    return vec4<f32>(mix(c.rgb, band * (luma(c.rgb) * 1.5 + 0.05), k * 0.6), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 60)], category="Party", shelves=PARTY, intensity="strength"),
cl("trippy", "Trippy", 14, "Psychedelic: the colours swirl and the picture melts.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let off = vec2<f32>(sin(uv.y * 8.0 + t), cos(uv.x * 7.0 + t * 1.2)) * 0.015;
    let c = sample(uv + off);
    let hue = turn_hue(c.rgb, (sin(uv.x * 4.0 + t) + cos(uv.y * 4.0 - t)) * 90.0 + t * 60.0);
    return vec4<f32>(saturation(hue, 1.5), c.a);
}
""", [p("speed", "Speed", 0, 100, 100)], category="Party", shelves=PARTY),
cl("orange-negative", "Orange Negative", 15, "An orange-tinted negative of the picture.", """
struct Params { speed: f32, color: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = clamp(to_display(c.rgb), vec3<f32>(0.0), vec3<f32>(1.0));
    let neg = from_display(vec3<f32>(1.0) - d);
    let k = params.color / 100.0;
    let l = luma(neg);
    let orange = vec3<f32>(l * 1.6, l * 0.75, l * 0.2);
    let pulse = 0.85 + 0.15 * sin(frame.time * rate() * 3.0);
    return vec4<f32>(mix(neg, orange, k) * pulse, c.a);
}
""", [SPEED, p("color", "Tint", 0, 100, 100)]),
cl("color-negative", "Color Negative", 16, "The picture as a colour negative.", """
struct Params { speed: f32, color: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = clamp(to_display(c.rgb), vec3<f32>(0.0), vec3<f32>(1.0));
    let neg = from_display(vec3<f32>(1.0) - d);
    let k = params.color / 100.0 * (0.85 + 0.15 * sin(frame.time * rate() * 3.0));
    return vec4<f32>(mix(c.rgb, neg, k), c.a);
}
""", [SPEED, p("color", "Strength", 0, 100, 100)], intensity="color"),
cl("alt-bw", "Alt. B&W", 17, "A punchy, high-contrast black and white.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let l = luma(c.rgb * vec3<f32>(1.2, 1.0, 0.7));
    return vec4<f32>(mix(c.rgb, contrast(vec3<f32>(l), 1.5), params.strength / 100.0), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], category="Black & White", intensity="strength"),
cl("bw-sketch", "B&W Sketch", 18, "The picture drawn as a pencil sketch on paper.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let e = edge_at(uv);
    let l = luma(c.rgb);
    let hatch = step(0.5, fract((uv.x + uv.y) * frame.size.y / 4.0)) * (1.0 - smoothstep(0.1, 0.5, l)) * 0.3;
    let ink = clamp(1.0 - e * 2.5 - hatch, 0.0, 1.0);
    let paper = vec3<f32>(0.95, 0.93, 0.88) * ink;
    // A highlight past white stays past it on the paper.
    return vec4<f32>(mix(c.rgb, paper, params.strength / 100.0) + max(c.rgb - vec3<f32>(1.0), vec3<f32>(0.0)), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], category="Stylize", intensity="strength"),
cl("painting", "Painting", 19, "The picture painted in soft daubs of colour, edges inked.", """
struct Params { texture: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let n = vec2<f32>(fbm(uv * 30.0), fbm(uv * 30.0 + vec2<f32>(5.0))) - vec2<f32>(0.5);
    let daub = soften(uv + n * 0.006, 4.0);
    let levels = 6.0;
    let poster = floor(clamp(daub, vec3<f32>(0.0), vec3<f32>(1.0)) * levels + 0.5) / levels;
    let ink = 1.0 - edge_at(uv) * 0.6;
    let rgb = mix(c.rgb, saturation(poster, 1.2) * ink, params.texture / 100.0) + max(c.rgb - vec3<f32>(1.0), vec3<f32>(0.0));
    return vec4<f32>(rgb, c.a);
}
""", [p("texture", "Strength", 0, 100, 100)], category="Stylize", intensity="texture"),
cl("cold-lab", "Cold Lab", 20, "A cold, clinical blue-green grade with a faint flicker.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let flicker = 1.0 + (vnoise(vec2<f32>(frame.time * rate() * 10.0, 0.0)) - 0.5) * 0.1;
    let cold = mix(c.rgb, vec3<f32>(luma(c.rgb)) * vec3<f32>(0.75, 1.0, 1.1), 0.6);
    return vec4<f32>(mix(c.rgb, cold * flicker, k), c.a);
}
""", [SPEED, p("strength", "Strength", 0, 100, 100)], intensity="strength"),
cl("dark-night", "Dark Night", 21, "Day for night: a dark, blue-black grade with a little grain.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let night = mix(c.rgb, vec3<f32>(luma(c.rgb)), 0.5) * vec3<f32>(0.55, 0.65, 0.95) * 0.55 + grain_at(uv, 0.04);
    let vig = 1.0 - smoothstep(0.3, 0.9, length(uv - vec2<f32>(0.5)) * 1.2) * 0.5;
    return vec4<f32>(mix(c.rgb, night * vig, k), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], intensity="strength"),
cl("reversal-film", "Reversal Film", 22, "Slide film: rich, contrasty colour with deep blacks and grain.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let slide = s_curve(saturation(c.rgb, 1.3), 0.6) * vec3<f32>(1.0, 0.98, 1.04) + grain_at(uv, 0.05);
    return vec4<f32>(mix(c.rgb, slide, k), c.a);
}
""", [p("strength", "Strength", 0, 100, 70)], category="Retro", intensity="strength"),
cl("nineteen-98", "1998", 23, "A late-nineties snapshot: warm, soft and slightly faded.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let old = fade(c.rgb * vec3<f32>(1.08, 1.0, 0.86), 0.08) + grain_at(uv, 0.05);
    return vec4<f32>(mix(c.rgb, saturation(old, 0.9), k), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], category="Retro", intensity="strength"),
cl("retro-film", "Retro Film", 24, "Old film stock: faded colour, flicker, dust and scratches.", """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let t = floor(frame.time * (8.0 + rate() * 12.0));
    let flicker = 1.0 + (hash(vec2<f32>(t, 0.0), 1.0) - 0.5) * 0.12;
    let sx = hash(vec2<f32>(t, 1.0), 2.0);
    let scratch = smoothstep(0.0015, 0.0, abs(uv.x - sx)) * step(0.6, hash(vec2<f32>(t, 2.0), 2.0));
    let dust = step(0.998, hash(floor(uv * frame.size / 3.0), t));
    let old = fade(c.rgb * vec3<f32>(1.08, 0.98, 0.82), 0.06) * flicker;
    let rgb = mix(old, vec3<f32>(0.9), (scratch + dust) * 0.7);
    return vec4<f32>(mix(c.rgb, rgb, k), c.a);
}
""", [p("speed", "Speed", 0, 100, 30), p("strength", "Strength", 0, 100, 80)], category="Retro", intensity="strength"),
cl("girls-secrets", "Girl's Secrets", 25, "A soft, pastel pink grade with glowing highlights.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = params.strength / 100.0;
    let soft = soften(uv, 3.0);
    let pink = mix(c.rgb, max(c.rgb, soft), 0.5) * vec3<f32>(1.08, 0.95, 1.02) + vec3<f32>(0.05, 0.02, 0.04);
    return vec4<f32>(mix(c.rgb, pink, k), c.a);
}
""", [p("strength", "Strength", 0, 100, 100)], category="Love", intensity="strength"),
cl("radiating-love", "Radiating Love", 26, "Rings of pink love radiate out from the centre.", HEART + """
struct Params { speed: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(frame.size.x / frame.size.y, 1.0);
    let sd = heart_sdf(vec2<f32>(d.x, -d.y) * 2.0);
    let rings = pow(0.5 + 0.5 * sin(sd * 20.0 - frame.time * rate() * 6.0), 4.0) * smoothstep(1.2, 0.0, sd);
    let k = params.strength / 100.0;
    return vec4<f32>(c.rgb * mix(vec3<f32>(1.0), vec3<f32>(1.1, 0.9, 0.95), k) + vec3<f32>(1.0, 0.3, 0.5) * rings * 0.5 * k, c.a);
}
""", [p("speed", "Speed", 0, 100, 50), p("strength", "Strength", 0, 100, 100)], category="Love", intensity="strength"),
]
