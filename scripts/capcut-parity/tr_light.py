from lib_wgsl import *

PACKAGES = [
T("montage-snippets", "Montage Snippets", "Basic", 20,
  "Quick snippets of both shots cut back and forth, each landing with a punch-in and a flash, settling on the incoming shot.",
  """
struct Params { cuts: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.cuts, 2.0);
    let seg = min(floor(progress * n), n - 1.0);
    let local = fract(progress * n);
    // The first snippet is the outgoing shot, the last the incoming one,
    // and between them the incoming one wins more often as the cut goes on.
    var to_side = hash(vec2<f32>(seg, 3.0), 0.5) < mix(0.2, 0.9, progress);
    if (seg < 0.5) {
        to_side = false;
    }
    if (seg > n - 1.5) {
        to_side = true;
    }
    let env = sin(3.14159265 * progress);
    let z = 1.0 + 0.15 * (1.0 - local) * (1.0 - local) * env;
    let suv = (uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5);
    let c = select(from_at(suv), to_at(suv), to_side);
    let flash = exp(-local * 10.0) * 0.9 * env;
    return vec4<f32>(c.rgb + vec3<f32>(flash), c.a);
}
""", [p("cuts", "Snippets", 2, 12, 6, unit="")]),

T("then-and-now", "Then and Now", "Basic", 21,
  "The outgoing shot ages into an old sepia photograph, then a flash brings the incoming one in, in colour.",
  """
struct Params { age: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let a = from_at(uv);
    let b = to_at(uv);
    let k = params.age / 100.0;
    let l = luma(a.rgb);
    let sepia = vec3<f32>(l * 1.08, l * 0.82, l * 0.55);
    let old = mix(a.rgb, sepia * (0.85 + 0.15 * hash(floor(uv * frame.size), 2.0)), k);
    let first = smoothstep(0.0, 0.5, progress);
    let second = smoothstep(0.5, 1.0, progress);
    var c = mix(mix(a.rgb, old, first), b.rgb, second);
    let flash = exp(-pow((progress - 0.5) / 0.06, 2.0));
    c = c + vec3<f32>(flash * 1.2);
    return vec4<f32>(c, mix(a.a, b.a, second));
}
""", [p("age", "Age", 0, 100, 100)]),

T("dissolve-ii", "Dissolve II", "Dissolve", 22,
  "The incoming shot appears through the outgoing one grain by grain.",
  """
struct Params { grain: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let cell = max(params.grain, 1.0);
    let n = hash(floor(uv * frame.size / cell), 7.0);
    let m = smoothstep(n - 0.04, n + 0.04, progress * 1.08 - 0.04);
    return mix(from_at(uv), to_at(uv), m);
}
""", [p("grain", "Grain", 1, 32, 3, unit="px")]),

T("dissolve-iii", "Dissolve III", "Dissolve", 23,
  "The outgoing shot dissolves from its shadows to its highlights, the incoming one showing through the dark parts first.",
  """
struct Params { softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let a = from_at(uv);
    let l = clamp(to_display(vec3<f32>(luma(a.rgb))).x, 0.0, 1.0);
    let soft = max(params.softness / 100.0, 0.01);
    let edge = progress * (1.0 + 2.0 * soft) - soft;
    let m = smoothstep(l - soft, l + soft, edge);
    return mix(a, to_at(uv), m);
}
""", [p("softness", "Softness", 0, 100, 20)]),

T("gradient-wipe", "Gradient Wipe", "Wipe", 24,
  "A wide, soft gradient sweeps the incoming shot across the outgoing one.",
  """
struct Params { angle: f32, softness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let a = radians(params.angle);
    let dir = vec2<f32>(cos(a), sin(a));
    let reach = 0.5 * (abs(dir.x) + abs(dir.y));
    let coord = (dot(uv - vec2<f32>(0.5), dir) / reach) * 0.5 + 0.5;
    let soft = max(params.softness / 100.0, 0.01) * 0.6;
    let edge = progress * (1.0 + 2.0 * soft) - soft;
    let m = smoothstep(edge - soft, edge + soft, coord);
    return mix(to_at(uv), from_at(uv), m);
}
""", [p("angle", "Angle", 0, 360, 0, unit="°"), p("softness", "Softness", 0, 100, 60)]),

T("black-smoke", "Black Smoke", "Dissolve", 25,
  "Black smoke billows over the outgoing shot and clears from the incoming one.",
  NOISE + """
struct Params { density: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y) * 3.0;
    let n = fbm(q + vec2<f32>(progress * 1.2, -progress * 0.7));
    let e = sin(3.14159265 * progress);
    let cover = clamp((n + e * (0.6 + params.density / 100.0) - 1.0) / 0.25, 0.0, 1.0);
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.42, 0.58, progress));
    return vec4<f32>(mix(base.rgb, vec3<f32>(0.0), cover), base.a);
}
""", [p("density", "Density", 0, 100, 60)]),

T("white-smoke", "White Smoke", "Dissolve", 26,
  "White smoke billows over the outgoing shot and clears from the incoming one.",
  NOISE + """
struct Params { density: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let q = vec2<f32>(uv.x * aspect, uv.y) * 3.0;
    let n = fbm(q + vec2<f32>(-progress * 1.2, -progress * 0.7));
    let e = sin(3.14159265 * progress);
    let cover = clamp((n + e * (0.6 + params.density / 100.0) - 1.0) / 0.25, 0.0, 1.0);
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.42, 0.58, progress));
    return vec4<f32>(mix(base.rgb, vec3<f32>(0.9), cover), base.a);
}
""", [p("density", "Density", 0, 100, 60)]),

T("bw-flash", "B&W Flash", "Light", 27,
  "The cut strobes between black and white frames, both shots drained to black and white as it passes.",
  """
struct Params { flashes: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let e = sin(3.14159265 * progress);
    let grey = mix(base.rgb, vec3<f32>(luma(base.rgb)), smoothstep(0.0, 0.4, e));
    let n = max(params.flashes, 1.0) * 2.0;
    let k = floor(progress * n);
    let f = fract(progress * n);
    let flash = select(vec3<f32>(0.0), vec3<f32>(1.0), fract(k * 0.5) < 0.25);
    let amount = e * (1.0 - f) * 0.9;
    return vec4<f32>(mix(grey, flash, amount), base.a);
}
""", [p("flashes", "Flashes", 1, 8, 4, unit="")]),

T("rainbow-warp", "Rainbow Warp", "Distort", 28,
  "Both shots ripple and fringe with rainbow colour as one warps into the other.",
  RAINBOW + """
struct Params { warp: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let k = params.warp / 100.0;
    let off = vec2<f32>(sin(uv.y * 14.0 + progress * 12.0), cos(uv.x * 11.0 + progress * 9.0)) * 0.035 * e * k;
    let a = from_at(uv + off);
    let b = to_at(uv - off);
    let c = mix(a, b, smoothstep(0.3, 0.7, progress));
    let tint = rainbow(fract(uv.x * 1.3 + uv.y * 0.7 + progress * 2.0));
    let rgb = mix(c.rgb, c.rgb * 0.6 + tint * 0.7, e * 0.7 * k);
    return vec4<f32>(rgb, c.a);
}
""", [p("warp", "Warp", 0, 100, 70)]),

T("rgb-glitch", "RGB Glitch", "Glitch", 29,
  "The red, green and blue of both shots tear apart in steps and snap back together on the incoming one.",
  """
struct Params { split: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let step_t = floor(progress * 18.0);
    let band = floor(uv.y * 12.0);
    let jump = (hash(vec2<f32>(band, step_t), 4.0) - 0.5) * 0.08 * e;
    let o = vec2<f32>(params.split / 100.0 * 0.04 * e + jump, 0.0);
    let to_side = progress >= 0.5;
    var r: vec4<f32>;
    var g: vec4<f32>;
    var b: vec4<f32>;
    if (to_side) {
        r = to_at(uv + o);
        g = to_at(uv + vec2<f32>(jump, 0.0));
        b = to_at(uv - o);
    } else {
        r = from_at(uv + o);
        g = from_at(uv + vec2<f32>(jump, 0.0));
        b = from_at(uv - o);
    }
    return vec4<f32>(r.r, g.g, b.b, g.a);
}
""", [p("split", "Split", 0, 100, 60)]),

T("rainbow-filter", "Rainbow Filter", "Light", 30,
  "A sweep of rainbow light washes across the cut, its hues turning as one shot becomes the other.",
  RAINBOW + HUE + """
struct Params { strength: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let c = mix(from_at(uv), to_at(uv), smoothstep(0.25, 0.75, progress));
    let k = params.strength / 100.0 * e;
    let turned = turn_hue(c.rgb, 360.0 * progress);
    let wash = rainbow(fract(uv.x - progress * 1.5)) * luma(c.rgb) * 2.0;
    let rgb = mix(c.rgb, mix(turned, wash, 0.5), k);
    return vec4<f32>(rgb, c.a);
}
""", [p("strength", "Strength", 0, 100, 70)]),

T("urban-glitch", "Urban Glitch", "Glitch", 31,
  "Blocks of both shots shift, invert and stutter like a broken street screen before the incoming one settles.",
  """
struct Params { amount: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress) * params.amount / 100.0;
    let t = floor(progress * 24.0);
    let block = floor(uv * vec2<f32>(8.0, 14.0));
    let h = hash(block, t);
    let shift = select(0.0, (hash(block + vec2<f32>(5.0), t) - 0.5) * 0.3, h < e * 0.6);
    let suv = vec2<f32>(fract(uv.x + shift), uv.y);
    let pick = select(progress >= 0.5, hash(block, t + 9.0) < progress, e > 0.05);
    var c = select(from_at(suv), to_at(suv), pick);
    if (h > 1.0 - e * 0.2) {
        c = vec4<f32>(vec3<f32>(1.0) - min(c.rgb, vec3<f32>(1.0)), c.a);
    }
    let line = step(0.5, fract(uv.y * frame.size.y * 0.5)) * 0.15 * e;
    return vec4<f32>(c.rgb * (1.0 - line), c.a);
}
""", [p("amount", "Amount", 0, 100, 70)]),

T("camera-glow", "Camera Glow", "Light", 32,
  "The outgoing shot blooms into a soft, bright glow, as a lens does facing the light, and the incoming one comes out of it.",
  DISCBLUR + """
struct Params { glow: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let r = 0.03 * e;
    let m = smoothstep(0.4, 0.6, progress);
    let soft = mix(disc_from(uv, r), disc_to(uv, r), m);
    let sharp = mix(from_at(uv), to_at(uv), m);
    let k = params.glow / 100.0;
    let rgb = mix(sharp.rgb, soft.rgb, e) * (1.0 + e * 1.5 * k) + soft.rgb * e * k;
    return vec4<f32>(rgb, sharp.a);
}
""", [p("glow", "Glow", 0, 100, 60)]),

T("light-sweep", "Light Sweep II", "Light", 33,
  "A bright band of light sweeps diagonally across, carrying the incoming shot behind it.",
  """
struct Params { width: f32, warmth: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let coord = (uv.x + uv.y * 0.6) / 1.6;
    let w = max(params.width / 100.0, 0.01) * 0.15;
    let edge = progress * (1.0 + 4.0 * w) - 2.0 * w;
    let m = smoothstep(edge - 0.01, edge + 0.01, coord);
    let base = mix(to_at(uv), from_at(uv), m);
    let band = exp(-pow((coord - edge) / w, 2.0)) * 3.0;
    let tint = mix(vec3<f32>(0.9, 0.95, 1.0), vec3<f32>(1.0, 0.8, 0.55), params.warmth / 100.0);
    return vec4<f32>(base.rgb + tint * band, base.a);
}
""", [p("width", "Width", 0, 100, 40), p("warmth", "Warmth", 0, 100, 40)]),

T("flash-transition", "Flash", "Light", 34,
  "A camera flash overexposes the cut for an instant.",
  """
struct Params { brightness: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = select(from_at(uv), to_at(uv), progress >= 0.5);
    let e = exp(-pow((progress - 0.5) / 0.16, 2.0));
    let k = params.brightness / 100.0;
    let rgb = base.rgb * (1.0 + e * 8.0 * k) + vec3<f32>(e * 0.8 * k);
    return vec4<f32>(rgb, base.a);
}
""", [p("brightness", "Brightness", 0, 100, 70)]),

T("light-beam", "Light Beam", "Light", 35,
  "Shafts of light sweep across the frame as the shots cross.",
  """
struct Params { beams: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.35, 0.65, progress));
    let e = sin(3.14159265 * progress);
    let n = i32(max(params.beams, 1.0));
    var light = 0.0;
    for (var i = 0; i < 8; i++) {
        if (i >= n) {
            break;
        }
        let fi = f32(i);
        let x = hash(vec2<f32>(fi, 1.0), 3.0) * 1.6 - 0.3 + (progress - 0.5) * (0.6 + fi * 0.2);
        let slant = (hash(vec2<f32>(fi, 2.0), 3.0) - 0.5) * 0.8;
        let d = uv.x - x - (uv.y - 0.5) * slant;
        let w = 0.02 + 0.05 * hash(vec2<f32>(fi, 4.0), 3.0);
        light += exp(-d * d / (w * w));
    }
    let rgb = base.rgb + vec3<f32>(1.0, 0.95, 0.85) * light * e * 1.4;
    return vec4<f32>(rgb, base.a);
}
""", [p("beams", "Beams", 1, 8, 4, unit="")]),

T("blanch", "Blanch", "Light", 36,
  "The outgoing shot bleaches out to a washed white and the incoming one develops back out of it.",
  """
struct Params { strength: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let base = mix(from_at(uv), to_at(uv), smoothstep(0.45, 0.55, progress));
    let e = sin(3.14159265 * progress) * params.strength / 100.0;
    let pale = mix(base.rgb, vec3<f32>(luma(base.rgb)), e * 0.8);
    let lifted = vec3<f32>(1.0) - (vec3<f32>(1.0) - min(pale, vec3<f32>(1.0))) * (1.0 - e);
    return vec4<f32>(lifted, base.a);
}
""", [p("strength", "Strength", 0, 100, 90)]),

T("blurred-highlight", "Blurred Highlight", "Light", 37,
  "The highlights of both shots bloom and blur together as one gives way to the other.",
  DISCBLUR + """
struct Params { bloom: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let m = smoothstep(0.3, 0.7, progress);
    let soft = mix(disc_from(uv, 0.04 * e), disc_to(uv, 0.04 * e), m);
    let sharp = mix(from_at(uv), to_at(uv), m);
    let bright = max(soft.rgb - vec3<f32>(0.5), vec3<f32>(0.0)) * 3.0;
    let rgb = mix(sharp.rgb, soft.rgb, e * 0.7) + bright * e * params.bloom / 100.0;
    return vec4<f32>(rgb, sharp.a);
}
""", [p("bloom", "Bloom", 0, 100, 70)]),

T("lightning-transition", "Lightning", "Light", 38,
  "A bolt of lightning cracks down the frame and the incoming shot is there in its flash.",
  NOISE + """
struct Params { glow: f32 }

fn bolt(uv: vec2<f32>, seed: f32) -> f32 {
    let x = 0.5 + (fbm(vec2<f32>(uv.y * 4.0, seed)) - 0.5) * 0.5 + (vnoise(vec2<f32>(uv.y * 30.0, seed)) - 0.5) * 0.04;
    let d = abs(uv.x - x) * frame.size.x / frame.size.y;
    return 0.002 / (d + 0.002);
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let to_side = progress >= 0.5;
    let base = select(from_at(uv), to_at(uv), to_side);
    let strike = exp(-pow((progress - 0.5) / 0.08, 2.0)) + 0.5 * exp(-pow((progress - 0.35) / 0.03, 2.0));
    let dark = sin(3.14159265 * progress) * 0.6;
    let night = base.rgb * (1.0 - dark) * vec3<f32>(0.8, 0.85, 1.1);
    let b = bolt(uv, floor(progress * 6.0)) * strike;
    let k = params.glow / 100.0;
    let rgb = night + vec3<f32>(0.7, 0.8, 1.0) * (b * 3.0 + strike * 0.8 * k);
    return vec4<f32>(rgb, base.a);
}
""", [p("glow", "Glow", 0, 100, 60)]),

T("strobe-transition", "Strobe", "Light", 39,
  "The two shots strobe against each other, faster and faster, ending on the incoming one.",
  """
struct Params { rate: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.rate, 2.0);
    let phase = progress * progress * n;
    let on = fract(phase) < 0.5;
    var c = select(from_at(uv), to_at(uv), on);
    if (progress > 0.9) {
        c = to_at(uv);
    }
    let flash = (1.0 - fract(phase * 2.0)) * 0.5 * sin(3.14159265 * progress);
    return vec4<f32>(c.rgb + vec3<f32>(flash), c.a);
}
""", [p("rate", "Rate", 2, 16, 8, unit="")]),

T("twinkle-zoom", "Twinkle Zoom", "Zoom", 40,
  "The outgoing shot zooms in with a burst of twinkling stars and the incoming one zooms back out of it.",
  GLINT + """
struct Params { sparkle: f32 }

fn zoom_from(uv: vec2<f32>, z: f32) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 8; i++) {
        let s = z * (1.0 + f32(i) * 0.02 * (z - 1.0));
        sum += from_at((uv - vec2<f32>(0.5)) / s + vec2<f32>(0.5));
    }
    return sum / 8.0;
}

fn zoom_to(uv: vec2<f32>, z: f32) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = 0; i < 8; i++) {
        let s = z * (1.0 + f32(i) * 0.02 * (z - 1.0));
        sum += to_at((uv - vec2<f32>(0.5)) / s + vec2<f32>(0.5));
    }
    return sum / 8.0;
}

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    var c: vec4<f32>;
    if (progress < 0.5) {
        c = zoom_from(uv, 1.0 + progress * 2.0);
    } else {
        c = zoom_to(uv, 1.0 + (1.0 - progress) * 2.0);
    }
    let cells = vec2<f32>(9.0, 9.0 * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(hash(cell, 1.0), hash(cell, 2.0))) / cells;
    let size = 0.6 / cells.x * (0.5 + hash(cell, 3.0));
    let twinkle = 0.5 + 0.5 * sin(progress * 30.0 + hash(cell, 4.0) * 6.28);
    let d = (uv - centre) * vec2<f32>(1.0, frame.size.y / frame.size.x);
    let star = glint(d, size) * twinkle * e * params.sparkle / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.95, 0.8) * star * 2.0 + vec3<f32>(e * e * 0.3), c.a);
}
""", [p("sparkle", "Sparkle", 0, 100, 70)]),

T("transform-shimmer", "Transform Shimmer", "Light", 41,
  "A shimmer of glints passes over the frame as the outgoing shot transforms into the incoming one.",
  GLINT + """
struct Params { shimmer: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let z = 1.0 + 0.08 * e;
    let suv = (uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5);
    let wave = smoothstep(progress - 0.25, progress + 0.25, uv.x * 0.7 + uv.y * 0.3);
    let c = mix(to_at(suv), from_at(suv), wave);
    let cells = vec2<f32>(14.0, 14.0 * frame.size.y / frame.size.x);
    let cell = floor(uv * cells);
    let centre = (cell + vec2<f32>(hash(cell, 5.0), hash(cell, 6.0))) / cells;
    let live = exp(-pow((uv.x * 0.7 + uv.y * 0.3 - progress) / 0.12, 2.0));
    let d = (uv - centre) * vec2<f32>(1.0, frame.size.y / frame.size.x);
    let star = glint(d, 0.5 / cells.x * (0.4 + hash(cell, 7.0))) * live * params.shimmer / 100.0;
    return vec4<f32>(c.rgb + vec3<f32>(1.0, 0.97, 0.9) * star * 2.5 + vec3<f32>(live * e * 0.15), c.a);
}
""", [p("shimmer", "Shimmer", 0, 100, 70)]),

T("vintage-screening", "Vintage Screening", "Light", 42,
  "A flickering old projector: the frame rolls, scratches and dust flash by, and the next reel begins.",
  """
struct Params { wear: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let roll = select(0.0, (progress - 0.5) * 2.0, abs(progress - 0.5) < 0.12) * e;
    let ruv = vec2<f32>(uv.x, fract(uv.y + roll));
    let base = select(from_at(ruv), to_at(ruv), progress >= 0.5);
    let k = params.wear / 100.0 * e;
    let l = luma(base.rgb);
    let sepia = mix(base.rgb, vec3<f32>(l * 1.05, l * 0.85, l * 0.6), k);
    let t = floor(progress * 30.0);
    let flicker = 1.0 + (hash(vec2<f32>(t, 0.0), 1.0) - 0.5) * 0.5 * k;
    let sx = hash(vec2<f32>(t, 1.0), 2.0);
    let scratch = smoothstep(0.002, 0.0, abs(uv.x - sx)) * step(0.5, hash(vec2<f32>(t, 2.0), 2.0));
    let dust = step(0.997, hash(floor(uv * frame.size / 3.0), t)) ;
    let bar = smoothstep(0.02, 0.0, abs(fract(uv.y + roll) - 0.0)) * step(0.01, abs(roll));
    var rgb = sepia * flicker * (1.0 - bar);
    rgb = mix(rgb, vec3<f32>(0.9), (scratch + dust) * k);
    return vec4<f32>(rgb, base.a);
}
""", [p("wear", "Wear", 0, 100, 80)]),
]

# Smoke and bleach cover the frame at their peak; the card shows them coming.
for spec in PACKAGES:
    if spec["slug"] in ("black-smoke", "white-smoke", "blanch"):
        spec["card"] = {"progress": 0.22}
