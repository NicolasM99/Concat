from lib_wgsl import *

# Coverage of one particle at `p`, the particle's own coordinates (its
# radius 1), `t` its age in seconds for shapes that move on their own.
SHAPES = {
    "dot": "return smoothstep(1.0, 0.55, length(p));",
    "glow": "return exp(-dot(p, p) * 3.0);",
    "bokeh": "let d = length(p); return smoothstep(1.0, 0.9, d) * (0.55 + 0.45 * smoothstep(0.6, 1.0, d));",
    "bubble": "let d = length(p); return smoothstep(1.0, 0.92, d) * (0.15 + 0.85 * smoothstep(0.75, 0.95, d)) + exp(-dot(p - vec2<f32>(-0.4, -0.4), p - vec2<f32>(-0.4, -0.4)) * 30.0);",
    "glint": "let a = abs(p); return max(0.0, 1.0 - (a.x * 6.0 + a.y)) + max(0.0, 1.0 - (a.y * 6.0 + a.x)) + exp(-dot(p, p) * 20.0);",
    "streak": "return exp(-p.x * p.x * 60.0) * smoothstep(1.0, 0.0, abs(p.y));",
    "heart": "let q = vec2<f32>(p.x, -p.y) * 0.9; let p2 = vec2<f32>(abs(q.x), q.y + 0.55); var d: f32; if (p2.y + p2.x > 1.0) { d = length(p2 - vec2<f32>(0.25, 0.75)) - 0.35355; } else { let tt = max(p2.x + p2.y, 0.0) * 0.5; d = sqrt(min(dot(p2 - vec2<f32>(0.0, 1.0), p2 - vec2<f32>(0.0, 1.0)), dot(p2 - vec2<f32>(tt), p2 - vec2<f32>(tt)))) * sign(p2.x - p2.y); } return smoothstep(0.04, -0.04, d);",
    "petal": "let q = vec2<f32>(p.x * 1.0, p.y * 1.9 + 0.2 * p.x * p.x); return smoothstep(1.0, 0.8, length(q)) * (0.8 + 0.2 * p.y);",
    "square": "let q = abs(p * vec2<f32>(1.0, 1.7)); return smoothstep(0.9, 0.8, max(q.x, q.y));",
    "feather": "let q = vec2<f32>(p.x * 3.0, p.y * 0.85); let vane = smoothstep(1.0, 0.85, length(q)) * (0.7 + 0.3 * abs(sin(p.y * 30.0))); let quill = exp(-p.x * p.x * 400.0) * step(abs(p.y), 1.05); return max(vane, quill * 0.8);",
    "snowflake": "let r = length(p); let a = atan2(p.y, p.x); let arm = abs(fract(a / 1.0471976 + 0.5) - 0.5) * r * 6.2832; let spokes = exp(-arm * arm * 6.0) * smoothstep(1.0, 0.8, r); let tips = exp(-pow(abs(fract(a / 1.0471976 + 0.5) - 0.5) * 8.0, 2.0)) * exp(-pow((r - 0.6) * 6.0, 2.0)); return clamp(spokes + tips * 0.5 + exp(-r * r * 30.0), 0.0, 1.0);",
    "star5": "let r = length(p); let a = atan2(p.x, -p.y); let k = abs(fract(a / 1.2566371 + 0.5) - 0.5) * 2.0; let edge = mix(0.42, 1.0, pow(1.0 - k, 2.0)); return smoothstep(edge, edge - 0.08, r);",
    "diamond": "let q = abs(p); return smoothstep(1.0, 0.85, q.x * 1.4 + q.y) * (0.6 + 0.4 * step(0.0, p.x * p.y));",
    "butterfly": "let flap = 0.35 + 0.65 * abs(sin(t * 9.0)); let q = vec2<f32>(abs(p.x) / max(flap, 0.05), p.y); let upper = smoothstep(1.0, 0.85, length((q - vec2<f32>(0.5, -0.3)) * vec2<f32>(1.6, 1.8))); let lower = smoothstep(1.0, 0.85, length((q - vec2<f32>(0.4, 0.35)) * vec2<f32>(2.2, 2.4))); let body = exp(-p.x * p.x * 300.0) * step(abs(p.y), 0.6); return max(max(upper, lower), body);",
    "note": "let head = smoothstep(1.0, 0.85, length((p - vec2<f32>(-0.2, 0.55)) * vec2<f32>(2.4, 3.2))); let stem = step(abs(p.x - 0.18), 0.06) * step(-0.8, p.y) * step(p.y, 0.55); let flag = smoothstep(0.12, 0.0, abs(p.y + 0.6 + (p.x - 0.18) * 0.8)) * step(0.18, p.x) * step(p.x, 0.6); return max(max(head, stem), flag);",
}

PALETTES = {
    "white": "return vec3<f32>(1.0);",
    "snow": "return mix(vec3<f32>(0.85, 0.92, 1.0), vec3<f32>(1.0), h);",
    "gold": "return mix(vec3<f32>(1.0, 0.62, 0.18), vec3<f32>(1.0, 0.86, 0.45), h);",
    "pink": "return mix(vec3<f32>(1.0, 0.45, 0.65), vec3<f32>(1.0, 0.78, 0.86), h);",
    "red": "return mix(vec3<f32>(0.95, 0.05, 0.18), vec3<f32>(1.0, 0.35, 0.5), h);",
    "rainbow": "let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67))); return c * c;",
    "warm": "return mix(vec3<f32>(1.0, 0.35, 0.05), vec3<f32>(1.0, 0.8, 0.3), h);",
    "ember": "return mix(vec3<f32>(1.0, 0.25, 0.02), vec3<f32>(1.0, 0.6, 0.15), h);",
    "firefly": "return mix(vec3<f32>(0.75, 1.0, 0.25), vec3<f32>(1.0, 0.9, 0.35), h);",
    "rain": "return vec3<f32>(0.7, 0.8, 0.95);",
    "blue": "return mix(vec3<f32>(0.3, 0.55, 1.0), vec3<f32>(0.7, 0.85, 1.0), h);",
    "violet": "return mix(vec3<f32>(0.45, 0.35, 1.0), vec3<f32>(0.95, 0.5, 1.0), h);",
    "xmas": "if (h < 0.34) { return vec3<f32>(1.0, 0.8, 0.25); } if (h < 0.67) { return vec3<f32>(0.9, 0.08, 0.1); } return vec3<f32>(0.1, 0.7, 0.25);",
    "pastel": "let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67))); return mix(c * c, vec3<f32>(1.0), 0.5);",
    "sakura": "return mix(vec3<f32>(1.0, 0.6, 0.75), vec3<f32>(1.0, 0.9, 0.94), h);",
}

# Whole-picture looks that go with a field, applied to the clip before the
# particles; `k` is the look's strength 0..1.
LOOKS = {
    "": "return rgb;",
    "night": "return rgb * mix(1.0, 0.55, k) * mix(vec3<f32>(1.0), vec3<f32>(0.8, 0.85, 1.1), k);",
    "rain": "return mix(rgb, vec3<f32>(luma(rgb)) * vec3<f32>(0.75, 0.85, 1.0), k * 0.6) * mix(1.0, 0.8, k);",
    "warm": "return rgb * mix(vec3<f32>(1.0), vec3<f32>(1.12, 0.98, 0.82), k);",
    "pink": "return mix(rgb, rgb * vec3<f32>(1.1, 0.9, 1.0) + vec3<f32>(0.05, 0.0, 0.03), k);",
    "cool": "return mix(rgb, rgb * vec3<f32>(0.9, 0.97, 1.12), k);",
    "violet": "return mix(rgb, rgb * vec3<f32>(0.95, 0.85, 1.15) + vec3<f32>(0.02, 0.0, 0.05), k);",
    "dream": "return mix(rgb, mix(rgb, vec3<f32>(luma(rgb)), 0.2) * vec3<f32>(1.0, 0.95, 1.08) + vec3<f32>(0.04), k);",
    "dark": "return rgb * mix(1.0, 0.4, k);",
    "gold": "return mix(rgb, rgb * vec3<f32>(1.1, 1.0, 0.8), k);",
}

TEMPLATE = """
struct Params { speed: f32, density: f32, size: f32, look: f32 }

// A field of particles drawn over the clip in three depths. Each depth is a
// grid that drifts with time; a cell holds at most one particle, placed,
// sized, turned and coloured by the cell's hash.

fn shape(p: vec2<f32>, t: f32) -> f32 {
    SHAPE
}

fn palette(h: f32) -> vec3<f32> {
    PALETTE
}

fn scene_look(rgb: vec3<f32>, k: f32) -> vec3<f32> {
    LOOK
}

fn depth(uv: vec2<f32>, scale: f32, seed: f32, t: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    var q = (vec2<f32>(uv.x * aspect, uv.y) - CENTRE) * scale;
    QWARP
    q = q - VELOCITY * t * scale * 0.1;
    q.x = q.x + sin(q.y * 0.6 + seed * 3.0 + t * 0.7) * SWAY;
    let cell = floor(q);
    if (hash(cell, seed) > params.density / 100.0 * DENSITY) {
        return vec4<f32>(0.0);
    }
    let centre = vec2<f32>(0.25) + vec2<f32>(hash(cell, seed + 1.0), hash(cell, seed + 2.0)) * 0.5;
    let r = (0.3 + 0.7 * hash(cell, seed + 3.0)) * params.size / 100.0 * RADIUS;
    let spin = (hash(cell, seed + 5.0) - 0.5) * 6.2831853 + t * SPIN * (hash(cell, seed + 6.0) - 0.5) * 2.0;
    let d = fract(q) - centre;
    let s = sin(spin);
    let c = cos(spin);
    let p = vec2<f32>(d.x * c - d.y * s, d.x * s + d.y * c) / max(r, 1e-4);
    if (dot(p, p) > 9.0) {
        return vec4<f32>(0.0);
    }
    let twinkle = mix(1.0, 0.5 + 0.5 * sin(t * 5.0 + hash(cell, seed + 7.0) * 6.2831853), TWINKLE);
    let cover = clamp(shape(p, t + hash(cell, seed + 8.0) * 10.0), 0.0, 1.0) * twinkle;
    return vec4<f32>(palette(hash(cell, seed + 4.0)) * cover, cover);
}

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let t = frame.time * (0.2 + params.speed / 100.0 * 2.4);
    var rgb = scene_look(c.rgb, params.look / 100.0);
    var alpha = c.a;
    let near = depth(uv, SCALE * 0.6, 11.0, t * 1.3);
    let mid = depth(uv, SCALE, 23.0, t);
    let far = depth(uv, SCALE * 1.7, 37.0, t * 0.7);
    var fields = array<vec4<f32>, 3>(far * 0.55, mid * 0.8, near);
    for (var i = 0; i < 3; i++) {
        let f = fields[i];
        rgb = BLEND;
        alpha = max(alpha, f.a);
    }
    return vec4<f32>(rgb, alpha);
}
"""

BLENDS = {
    "over": "rgb * (1.0 - f.a) + f.rgb * GAIN",
    "add": "rgb + f.rgb * GAIN",
}


def field(slug, name, order, description, shape, palette, *, velocity=(0.0, -1.0), sway=0.0, spin=0.0,
          twinkle=0.0, blend="over", gain=1.0, density=0.5, radius=0.35, scale=6.0, look="",
          look_default=0, speed=33, centre=(0.0, 0.0), qwarp="", category="Nature", shelves=None,
          density_default=60, size_default=60):
    v = f"vec2<f32>({float(velocity[0])}, {float(-velocity[1])})"  # y down in uv
    wgsl = (TEMPLATE
            .replace("SHAPE", SHAPES[shape])
            .replace("PALETTE", PALETTES[palette])
            .replace("LOOK", LOOKS[look])
            .replace("BLEND", BLENDS[blend])
            .replace("GAIN", f"{float(gain)}")
            .replace("VELOCITY", v)
            .replace("SWAY", f"{float(sway)}")
            .replace("SPIN", f"{float(spin)}")
            .replace("TWINKLE", f"{float(twinkle)}")
            .replace("DENSITY", f"{float(density) * 2.0}")
            .replace("RADIUS", f"{float(radius)}")
            .replace("SCALE", f"{float(scale)}")
            .replace("CENTRE", f"vec2<f32>({float(centre[0])}, {float(centre[1])})")
            .replace("QWARP", qwarp))
    params = [
        p("speed", "Speed", 0, 100, speed),
        p("density", "Amount", 0, 100, density_default),
        p("size", "Size", 10, 100, size_default),
        p("look", "Background", 0, 100, look_default if look else 0),
    ]
    if not look:
        params = params[:3]
        wgsl = wgsl.replace("struct Params { speed: f32, density: f32, size: f32, look: f32 }",
                            "struct Params { speed: f32, density: f32, size: f32 }")
        wgsl = wgsl.replace("var rgb = scene_look(c.rgb, params.look / 100.0);", "var rgb = scene_look(c.rgb, 0.0);")
    return E(slug, name, category, order, description, wgsl, params, shelves=shelves or ["Party & Club"] if category == "Party" else shelves,
             intensity="density", card={"moment": 1.5})


# Spiral: the field turns about the centre, faster near it.
SPIRAL = "let rr = length(q); let ang = t * 0.4 + rr * 0.15; q = vec2<f32>(q.x * cos(ang) - q.y * sin(ang), q.x * sin(ang) + q.y * cos(ang));"

PACKAGES = [
    field("snowflakes", "Snowflakes", 10, "Six-armed snowflakes drift down, turning as they fall.",
          "snowflake", "snow", velocity=(0.1, -0.6), sway=0.25, spin=0.8, scale=5.0, radius=0.4, look="cool", look_default=40),
    field("snowfall", "Snowfall", 11, "Soft snow falls thick and steady across the picture.",
          "dot", "white", velocity=(0.15, -1.0), sway=0.2, scale=9.0, radius=0.18, density=0.7, look="cool", look_default=30),
    field("rainfall", "Rain", 12, "Slanted streaks of rain over a cooler, darker picture.",
          "streak", "rain", velocity=(0.6, -6.0), scale=10.0, radius=0.5, density=0.5, look="rain", look_default=60, speed=50),
    field("cherry-blossom", "Cherry Blossom", 13, "Pink petals tumble down on a gentle breeze.",
          "petal", "sakura", velocity=(0.4, -0.7), sway=0.4, spin=1.5, scale=5.0, radius=0.35, look="pink", look_default=40),
    field("feathers", "Feathers", 14, "White feathers float slowly down, rocking side to side.",
          "feather", "white", velocity=(0.1, -0.4), sway=0.5, spin=0.7, scale=3.5, radius=0.45, density=0.35, look="dream", look_default=30),
    field("pink-hearts", "Pink Hearts", 15, "Pink hearts rise up through the picture.",
          "heart", "pink", velocity=(0.0, 0.6), sway=0.3, spin=0.3, scale=5.0, radius=0.35, look="pink", look_default=40, category="Love"),
    field("heart-kisses", "Heart Kisses", 16, "Red hearts float up and pulse over a warm, rosy picture.",
          "heart", "red", velocity=(0.0, 0.8), sway=0.2, twinkle=0.6, scale=4.5, radius=0.4, look="pink", look_default=60, category="Love"),
    field("firefly", "Firefly", 17, "Fireflies wander and glow over a darkened scene.",
          "glow", "firefly", velocity=(0.15, 0.1), sway=0.6, twinkle=0.9, blend="add", gain=1.6, scale=5.0, radius=0.25, density=0.35, look="night", look_default=60),
    field("starry", "Starry", 18, "Stars twinkle all over the picture.",
          "glint", "white", velocity=(0.0, 0.0), twinkle=1.0, blend="add", gain=1.5, scale=6.0, radius=0.3, density=0.45, look="night", look_default=30, category="Sparkle"),
    field("mini-stars", "Mini Stars", 19, "Tiny white stars glint here and there.",
          "glint", "white", velocity=(0.05, 0.05), twinkle=1.0, blend="add", gain=1.4, scale=10.0, radius=0.2, density=0.4, category="Sparkle"),
    field("mini-stars-ii", "Mini stars II", 20, "Tiny golden stars glint and drift.",
          "glint", "gold", velocity=(0.05, 0.15), twinkle=1.0, blend="add", gain=1.4, scale=10.0, radius=0.2, density=0.45, category="Sparkle"),
    field("star-rain", "Star Rain", 21, "Glinting stars fall in streaks like a shower of light.",
          "glint", "white", velocity=(0.6, -2.0), twinkle=0.6, blend="add", gain=1.5, scale=6.0, radius=0.3, density=0.35, category="Sparkle"),
    field("star-rain-2", "Star Rain 2", 22, "Golden stars fall in a glittering shower.",
          "glint", "gold", velocity=(0.4, -1.6), twinkle=0.6, blend="add", gain=1.5, scale=6.0, radius=0.3, density=0.4, category="Sparkle"),
    field("constellation", "Constellation", 23, "A night sky of points of light that twinkle slowly.",
          "glow", "blue", velocity=(0.03, 0.0), twinkle=1.0, blend="add", gain=2.0, scale=8.0, radius=0.12, density=0.5, look="night", look_default=50, category="Sparkle"),
    field("gold-sparkles", "Gold Sparkles", 24, "Gold sparkles glint and wink over a warmer picture.",
          "glint", "gold", velocity=(0.0, 0.2), twinkle=1.0, blend="add", gain=1.6, scale=7.0, radius=0.28, density=0.45, look="gold", look_default=40, category="Sparkle"),
    field("gold-dust", "Gold Dust", 25, "Fine gold dust floats up through the light.",
          "glow", "gold", velocity=(0.1, 0.35), sway=0.4, twinkle=0.7, blend="add", gain=1.4, scale=12.0, radius=0.15, density=0.5, category="Sparkle"),
    field("gold-sequins", "Gold Sequins", 26, "Gold sequins tumble down, flashing as they turn.",
          "diamond", "gold", velocity=(0.2, -0.9), sway=0.3, spin=2.0, twinkle=0.8, scale=6.0, radius=0.3, density=0.45, category="Sparkle"),
    field("xmas-stars", "Xmas Stars", 27, "Red, green and gold stars fall for the holidays.",
          "star5", "xmas", velocity=(0.1, -0.7), sway=0.3, spin=1.0, scale=5.0, radius=0.4, density=0.4, category="Party"),
    field("confetti-ii", "Confetti II", 28, "Colourful confetti flutters down, spinning.",
          "square", "rainbow", velocity=(0.2, -1.2), sway=0.4, spin=3.0, scale=7.0, radius=0.28, density=0.55, category="Party"),
    field("butterflies", "Butterflies", 29, "Colourful butterflies flutter across the picture.",
          "butterfly", "rainbow", velocity=(0.5, 0.25), sway=0.6, scale=3.5, radius=0.45, density=0.3),
    field("butterfly-dream", "Butterfly Dream", 30, "Glowing blue butterflies drift through a soft, dreamy haze.",
          "butterfly", "violet", velocity=(0.3, 0.3), sway=0.6, blend="add", gain=1.3, scale=3.5, radius=0.45, density=0.3, look="dream", look_default=60),
    field("spark", "Spark", 31, "Warm sparks glint and rise like embers.",
          "glint", "warm", velocity=(0.1, 1.0), sway=0.3, twinkle=0.8, blend="add", gain=1.6, scale=7.0, radius=0.25, density=0.4, look="warm", look_default=30, category="Light"),
    field("spark-2", "Spark 2", 32, "Glowing embers stream upward from below.",
          "glow", "ember", velocity=(0.2, 2.0), sway=0.5, twinkle=0.6, blend="add", gain=2.0, scale=10.0, radius=0.15, density=0.5, look="warm", look_default=40, category="Light"),
    field("rainbow-sparkle", "Rainbow Sparkle", 33, "Sparkles in every colour glint over the picture.",
          "glint", "rainbow", velocity=(0.0, 0.15), twinkle=1.0, blend="add", gain=1.6, scale=7.0, radius=0.28, density=0.45, category="Sparkle"),
    field("bubbles", "Bubbles", 34, "Soap bubbles rise and wobble through the picture.",
          "bubble", "pastel", velocity=(0.0, 0.5), sway=0.5, blend="add", gain=0.7, scale=4.0, radius=0.4, density=0.35),
    field("meteor", "Meteor", 35, "Meteors streak across the sky now and then.",
          "streak", "white", velocity=(3.0, -3.0), blend="add", gain=2.0, scale=3.0, radius=0.6, density=0.12, look="night", look_default=40, category="Sparkle"),
    field("wonderland", "Wonderland", 36, "A wonderland of glints and drifting light over a soft pink glow.",
          "glint", "pastel", velocity=(0.05, -0.3), sway=0.4, twinkle=1.0, blend="add", gain=1.5, scale=6.0, radius=0.28, density=0.45, look="pink", look_default=50, category="Sparkle"),
    field("sparkle-spiral", "Sparkle Spiral", 37, "Sparkles wheel round the centre of the picture in a spiral.",
          "glint", "gold", velocity=(0.0, 0.0), twinkle=0.8, blend="add", gain=1.6, scale=6.0, radius=0.28, density=0.45,
          centre=(0.889, 0.5), qwarp=SPIRAL, category="Sparkle"),
    field("iridescent", "Iridescent", 38, "Iridescent flecks shimmer over a pearly sheen.",
          "glint", "pastel", velocity=(0.1, 0.1), twinkle=1.0, blend="add", gain=1.3, scale=8.0, radius=0.22, density=0.45, look="dream", look_default=50, category="Sparkle"),
    field("milky-way-2", "Milky Way 2", 39, "A dense band of tiny stars over a violet night.",
          "glow", "white", velocity=(0.05, 0.0), twinkle=1.0, blend="add", gain=1.5, scale=16.0, radius=0.12, density=0.6, look="violet", look_default=50, category="Sparkle"),
    field("star", "Star", 40, "A few big stars shine over the picture.",
          "glint", "white", velocity=(0.0, 0.0), twinkle=0.5, blend="add", gain=1.6, scale=2.5, radius=0.4, density=0.35, speed=10, category="Sparkle"),
    field("color-diamond", "Color Diamond", 41, "Diamonds in every colour flash and turn.",
          "diamond", "rainbow", velocity=(0.0, 0.1), spin=1.0, twinkle=0.8, blend="add", gain=1.2, scale=5.0, radius=0.3, density=0.35, category="Sparkle"),
    field("polychromatic", "Polychromatic", 42, "Many-coloured glints sparkle all around.",
          "glint", "rainbow", velocity=(0.05, 0.05), twinkle=1.0, blend="add", gain=1.4, scale=9.0, radius=0.22, density=0.4, category="Sparkle"),
    field("daily", "Daily", 43, "Warm, soft bokeh circles float over the picture.",
          "bokeh", "warm", velocity=(0.05, 0.1), sway=0.3, blend="add", gain=0.45, scale=3.0, radius=0.45, density=0.4, look="warm", look_default=30, category="Light"),
    field("daily-2", "Daily 2", 44, "Pastel bokeh circles drift slowly across the picture.",
          "bokeh", "pastel", velocity=(0.08, 0.05), sway=0.3, blend="add", gain=0.45, scale=3.0, radius=0.45, density=0.4, category="Light"),
    field("daily-4", "Daily 4", 45, "Bokeh and little stars twinkle over a dreamy picture.",
          "bokeh", "white", velocity=(0.03, 0.08), sway=0.2, twinkle=0.6, blend="add", gain=0.5, scale=4.0, radius=0.35, density=0.4, look="dream", look_default=40, category="Light"),
    field("disco-ball", "Disco Ball 1", 46, "Spots of light from a mirror ball sweep the darkened room.",
          "glow", "white", velocity=(1.2, 0.0), twinkle=0.3, blend="add", gain=1.8, scale=5.0, radius=0.35, density=0.45, look="dark", look_default=50, category="Party"),
    field("heart-disco", "Heart Disco", 47, "Heart-shaped spots of coloured light sweep a darkened room.",
          "heart", "rainbow", velocity=(1.0, 0.2), twinkle=0.3, blend="add", gain=1.4, scale=4.0, radius=0.4, density=0.4, look="dark", look_default=50, category="Party"),
    field("musical-notes", "Musical Notes", 48, "Musical notes float up and away.",
          "note", "white", velocity=(0.2, 0.6), sway=0.4, spin=0.5, scale=4.0, radius=0.42, density=0.3, category="Party"),
    field("tree-shade", "Tree Shade", 49, "Dappled light through leaves plays slowly over the picture.",
          "bokeh", "warm", velocity=(0.05, 0.0), sway=0.6, blend="add", gain=0.35, scale=2.5, radius=0.55, density=0.55, look="dark", look_default=35, speed=15, category="Light"),
    field("tree-shade-2", "Tree Shade 2", 50, "Soft green-gold dapples of sunlight sway over the picture.",
          "glow", "firefly", velocity=(0.05, 0.02), sway=0.8, blend="add", gain=0.5, scale=3.0, radius=0.6, density=0.55, look="dark", look_default=35, speed=15, category="Light"),
    field("butterfly-color", "Butterfly Color", 51, "Bright butterflies in every colour flutter over a richer picture.",
          "butterfly", "rainbow", velocity=(0.4, 0.3), sway=0.7, scale=4.0, radius=0.42, density=0.35, look="pink", look_default=30),
]
