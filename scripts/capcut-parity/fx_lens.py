from lib_wgsl import *
from fx_camera import CLOCK, MOVE, SPEED

# The layer blurred in a disc of `r` pixels: two rings of taps about the
# point, premultiplied so a transparent edge does not bleed.
DISC = """
fn disc(uv: vec2<f32>, r: f32) -> vec4<f32> {
    let t = texel() * r;
    var sum = sample_premultiplied(uv);
    for (var i = 0; i < 16; i++) {
        let a = f32(i) * 0.3926991;
        let k = select(1.0, 0.55, i % 2 == 1);
        sum += sample_premultiplied(uv + vec2<f32>(cos(a), sin(a)) * t * k);
    }
    let m = sum / 17.0;
    return vec4<f32>(m.rgb / max(m.a, 1e-4), m.a);
}
"""

# The layer blurred along `d` (uv units), nine taps.
LINE = """
fn line_blur(uv: vec2<f32>, d: vec2<f32>) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += sample_premultiplied(uv + d * (f32(i) / 4.0));
    }
    let m = sum / 9.0;
    return vec4<f32>(m.rgb / max(m.a, 1e-4), m.a);
}
"""

def fx(slug, name, order, desc, body, params, category, **kw):
    clock = CLOCK if any(prm["key"] == "speed" for prm in params) else ""
    return E(slug, name, category, order, desc, clock + MOVE + DISC + LINE + body, params, **kw)

PACKAGES = [
fx("blur", "Blur", 10, "The whole picture softened out of focus.", """
struct Params { blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    return disc(uv, params.blur / 100.0 * frame.size.y * 0.03);
}
""", [p("blur", "Blur", 0, 100, 50)], "Blur", intensity="blur"),

fx("vertical-blur", "Vertical Blur", 11, "The picture smeared up and down.", """
struct Params { blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    return line_blur(uv, vec2<f32>(0.0, params.blur / 100.0 * 0.06));
}
""", [p("blur", "Blur", 0, 100, 50)], "Blur", intensity="blur"),

fx("camera-focus", "Camera Focus", 12, "The lens hunts for focus, drifting soft and sharp again.", """
struct Params { speed: f32, blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = 0.5 - 0.5 * cos(frame.time * rate() * 3.14159265);
    return disc(uv, k * params.blur / 100.0 * frame.size.y * 0.04);
}
""", [SPEED, p("blur", "Blur", 0, 100, 25)], "Blur", intensity="blur"),

fx("camera-focus-2", "Camera Focus 2", 13, "The clip opens out of focus and the lens pulls it sharp, zooming in a touch.", """
struct Params { speed: f32, blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = 1.0 - smoothstep(0.0, 1.0, opening());
    let q = moved(uv, vec2<f32>(0.0), 0.0, 1.0 + 0.05 * (1.0 - k));
    return disc(q, k * params.blur / 100.0 * frame.size.y * 0.05);
}
""", [SPEED, p("blur", "Blur", 0, 100, 50)], "Blur", intensity="blur", card={"moment": 0.4}),

fx("blurry-focus", "Blurry Focus", 14, "Only the middle of the picture stays sharp; the edges melt into blur.", """
struct Params { speed: f32, blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let breathe = 0.85 + 0.15 * sin(frame.time * rate() * 3.14159265);
    let d = length((uv - vec2<f32>(0.5)) * frame.size / frame.size.y);
    let k = smoothstep(0.15, 0.6, d) * breathe;
    return disc(uv, k * params.blur / 100.0 * frame.size.y * 0.06);
}
""", [SPEED, p("blur", "Blur", 0, 100, 25)], "Blur", intensity="blur"),

fx("pixel-blur", "Pixel Blur", 15, "The picture breaks into soft, shifting pixels.", """
struct Params { speed: f32, noise: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let size = mix(4.0, 40.0, params.noise / 100.0) * (0.7 + 0.3 * sin(frame.time * rate() * 3.0));
    let cells = frame.size / size;
    let q = (floor(uv * cells) + vec2<f32>(0.5)) / cells;
    let block = disc(q, size * 0.5);
    let c = sample(uv);
    return vec4<f32>(mix(c.rgb, block.rgb, 0.85), c.a);
}
""", [SPEED, p("noise", "Size", 0, 100, 50)], "Blur", intensity="noise"),

fx("chrome-blur", "Chrome Blur", 16, "A soft blur with its colours split, like light through cheap glass.", """
struct Params { blur: f32, chromatic: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let r = params.blur / 100.0 * frame.size.y * 0.03;
    let o = vec2<f32>(params.chromatic / 100.0 * 0.02, 0.0);
    let red = disc(uv + o, r);
    let green = disc(uv, r);
    let blue = disc(uv - o, r);
    return vec4<f32>(red.r, green.g, blue.b, green.a);
}
""", [p("blur", "Blur", 0, 100, 25), p("chromatic", "Split", 0, 100, 55)], "Blur", intensity="blur"),

fx("frosted-quality", "Frosted Quality", 17, "The picture seen through frosted glass: grainy, diffused, softly shimmering.", """
struct Params { speed: f32, strength: f32, noise: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0;
    let t = floor(frame.time * (2.0 + rate() * 6.0));
    let jitter = (vec2<f32>(hash(floor(uv * frame.size), t), hash(floor(uv * frame.size), t + 1.0)) - vec2<f32>(0.5)) * texel() * 12.0 * k;
    let c = disc(uv + jitter, 3.0 * k);
    let grain = (hash(floor(uv * frame.size * 0.5), t + 2.0) - 0.5) * params.noise / 100.0 * 0.2;
    return vec4<f32>(c.rgb * (1.0 + grain) + vec3<f32>(0.04 * k), c.a);
}
""", [p("speed", "Speed", 0, 100, 15), p("strength", "Strength", 0, 100, 50), p("noise", "Grain", 0, 100, 50)], "Blur", intensity="strength"),

fx("mosaic", "Mosaic", 18, "The picture as a mosaic of square tiles.", """
struct Params { size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let px = mix(4.0, frame.size.y / 12.0, params.size / 100.0);
    let cells = frame.size / px;
    return sample((floor(uv * cells) + vec2<f32>(0.5)) / cells);
}
""", [p("size", "Tile size", 0, 100, 50)], "Blur", intensity="size"),

fx("sharpen-edges", "Sharpen Edges", 19, "Edges crisped and darkened, as an over-sharpened camera draws them.", """
struct Params { sharpen: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let soft = soften(uv, 2.0);
    let k = params.sharpen / 100.0 * 3.0;
    let e = edge_at(uv);
    let rgb = c.rgb + (c.rgb - soft) * k - vec3<f32>(e * 0.15 * k);
    return vec4<f32>(rgb, c.a);
}
""", [p("sharpen", "Sharpen", 0, 100, 50)], "Blur", intensity="sharpen"),

fx("soft", "Soft", 20, "A gentle diffusion that lifts and softens the light.", """
struct Params { soft: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let b = disc(uv, frame.size.y * 0.012);
    let k = params.soft / 100.0;
    let glow = max(b.rgb, c.rgb);
    return vec4<f32>(mix(c.rgb, glow, k * 0.6) + b.rgb * 0.08 * k, c.a);
}
""", [p("soft", "Softness", 0, 100, 70)], "Blur", intensity="soft"),

fx("hazy", "Hazy", 21, "A milky haze over the picture, as on a humid day.", """
struct Params { blur: f32, haze: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let b = disc(uv, params.blur / 100.0 * frame.size.y * 0.02);
    let k = params.haze / 100.0;
    let rgb = mix(c.rgb, b.rgb, 0.6) * (1.0 - 0.3 * k) + vec3<f32>(0.18, 0.18, 0.2) * k;
    return vec4<f32>(rgb, c.a);
}
""", [p("blur", "Blur", 0, 100, 50), p("haze", "Haze", 0, 100, 50)], "Blur", intensity="haze"),

fx("backlit-focus", "Backlit Focus", 22, "A soft, backlit glow that drifts in and out of focus.", """
struct Params { speed: f32, soft: f32, blur: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = 0.5 - 0.5 * cos(frame.time * rate() * 3.14159265);
    let c = disc(uv, k * params.blur / 100.0 * frame.size.y * 0.03);
    let bloom = disc(uv, frame.size.y * 0.03);
    let light = max(bloom.rgb - vec3<f32>(0.4), vec3<f32>(0.0)) * 2.0 * params.soft / 100.0;
    return vec4<f32>(c.rgb + light * vec3<f32>(1.0, 0.92, 0.8), c.a);
}
""", [SPEED, p("soft", "Glow", 0, 100, 70), p("blur", "Blur", 0, 100, 33)], "Blur", intensity="soft"),

fx("white-diffusion", "White Diffusion", 23, "Bright light diffuses into a white bloom that breathes.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let c = sample(uv);
    let k = 0.6 + 0.4 * sin(frame.time * rate() * 3.14159265);
    let b = disc(uv, frame.size.y * 0.03);
    let rgb = screen(min(c.rgb, vec3<f32>(1.0)), b.rgb * 0.6 * k);
    return vec4<f32>(rgb + max(c.rgb - vec3<f32>(1.0), vec3<f32>(0.0)), c.a);
}
""", [SPEED], "Blur"),

# Lenses and distortion.
fx("fisheye-2", "Fisheye 2", 31, "A round fisheye view on black, the picture bent into a circle.", """
struct Params { distortion: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d) / 0.5;
    if (r > 1.0) {
        return vec4<f32>(0.0, 0.0, 0.0, 1.0);
    }
    let k = params.distortion / 100.0;
    let bent = mix(r, asin(clamp(r, 0.0, 1.0)) / 1.5707963, k);
    let q = select(d / (r * 0.5) * bent * 0.5, vec2<f32>(0.0), r < 1e-4) * frame.size.y / frame.size + vec2<f32>(0.5);
    let c = sample(q);
    return vec4<f32>(c.rgb * smoothstep(1.0, 0.97, r), c.a);
}
""", [p("distortion", "Distortion", 0, 100, 80)], "Distort", intensity="distortion"),

fx("fisheye-4", "Fisheye 4", 32, "A wide fisheye with a dark lens rim and a hint of glass texture.", """
struct Params { distortion: f32, rim: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(aspect, 1.0);
    let r = length(d);
    let k = params.distortion / 100.0;
    let q = d * (1.0 - k * 0.6 * r * r) / vec2<f32>(aspect, 1.0) + vec2<f32>(0.5);
    let c = sample(q);
    let rim = 1.0 - smoothstep(0.35, 0.85, r) * params.rim / 100.0;
    return vec4<f32>(c.rgb * rim, c.a);
}
""", [p("distortion", "Distortion", 0, 100, 60), p("rim", "Rim", 0, 100, 55)], "Distort", intensity="distortion"),

fx("wide-angle", "Wide Angle", 33, "A wide-angle lens: the edges stretched, the middle drawn in.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(aspect, 1.0);
    let r2 = dot(d, d);
    let k = params.strength / 100.0 * 0.5;
    let q = d * (1.0 - k + k * r2 * 1.5) / vec2<f32>(aspect, 1.0) + vec2<f32>(0.5);
    return sample(q);
}
""", [p("strength", "Strength", 0, 100, 45)], "Distort", intensity="strength"),

fx("magnifying-glass", "Magnifying Glass", 34, "A round magnifying glass enlarges one part of the picture.", """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let d = (uv - params.centre) * vec2<f32>(aspect, 1.0);
    let r = length(d);
    let radius = mix(0.1, 0.45, params.size / 100.0);
    if (r > radius) {
        let c = sample(uv);
        let shadow = 1.0 - 0.35 * exp(-(r - radius) / 0.02);
        return vec4<f32>(c.rgb * shadow, c.a);
    }
    let zoom = 1.0 + params.strength / 100.0 * 1.5;
    let bend = 1.0 - 0.3 * (r / radius) * (r / radius);
    let q = params.centre + d / (zoom * bend) / vec2<f32>(aspect, 1.0);
    let c = sample(q);
    let rim = smoothstep(radius - 0.006, radius, r);
    let glint = exp(-length(d - vec2<f32>(-radius * 0.45, -radius * 0.45)) / (radius * 0.15)) * 0.3;
    return vec4<f32>(mix(c.rgb, vec3<f32>(0.85), rim) + vec3<f32>(glint), c.a);
}
""", [{"key": "centre", "label": "Position", "type": "point", "default": 0.5}, p("size", "Size", 0, 100, 50), p("strength", "Zoom", 0, 100, 100)], "Distort", intensity="strength"),

fx("heart-magnifier", "Heart Magnifier", 35, "A heart-shaped lens enlarges part of the picture.", HEART + """
struct Params { centre: vec2<f32>, size: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let d = (uv - params.centre) * vec2<f32>(aspect, 1.0);
    let size = mix(0.15, 0.6, params.size / 100.0);
    let sd = heart_sdf(vec2<f32>(d.x, -d.y) / size) * size;
    if (sd > 0.0) {
        return sample(uv);
    }
    let zoom = 1.0 + params.strength / 100.0 * 1.5;
    let c = sample(params.centre + d / zoom / vec2<f32>(aspect, 1.0));
    let rim = smoothstep(-0.008, 0.0, sd);
    return vec4<f32>(mix(c.rgb, vec3<f32>(1.0, 0.45, 0.6), rim), c.a);
}
""", [{"key": "centre", "label": "Position", "type": "point", "default": 0.5}, p("size", "Size", 0, 100, 50), p("strength", "Zoom", 0, 100, 50)], "Distort", intensity="strength"),

fx("ripple", "Ripple", 36, "Rings ripple out across the picture as on the surface of water.", """
struct Params { speed: f32, distortion: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let waves = mix(10.0, 60.0, 1.0 - params.size / 100.0);
    let w = sin(r * waves - frame.time * rate() * 8.0) * params.distortion / 100.0 * 0.012;
    let q = uv + select(d / r, vec2<f32>(0.0), r < 1e-4) * w * frame.size.y / frame.size;
    let c = sample(q);
    return vec4<f32>(c.rgb * (1.0 + w * 8.0), c.a);
}
""", [p("speed", "Speed", 0, 100, 20), p("distortion", "Distortion", 0, 100, 55), p("size", "Size", 0, 100, 20)], "Distort", intensity="distortion"),

fx("ripples", "Ripples", 37, "Strong ripples ring out from the centre and bend the whole picture.", """
struct Params { speed: f32, distortion: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let w = sin(r * 25.0 - frame.time * rate() * 10.0) * params.distortion / 100.0 * 0.02 * exp(-r * 1.5);
    let q = uv + select(d / r, vec2<f32>(0.0), r < 1e-4) * w * frame.size.y / frame.size;
    return sample(q);
}
""", [SPEED, p("distortion", "Distortion", 0, 100, 100)], "Distort", intensity="distortion"),

fx("gentle-ripples", "Gentle Ripples", 38, "Gentle waves pass over the picture like a breeze over a pond.", """
struct Params { distortion: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.distortion / 100.0 * 0.008;
    let off = vec2<f32>(sin(uv.y * 30.0 + frame.time * 2.0), cos(uv.x * 25.0 + frame.time * 1.7)) * k;
    return sample(uv + off);
}
""", [p("distortion", "Distortion", 0, 100, 33)], "Distort", intensity="distortion"),

fx("rippling", "Rippling", 39, "The picture ripples in bands as through a heat haze.", """
struct Params { range: f32, strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0 * 0.02;
    let band = mix(4.0, 30.0, params.range / 100.0);
    let off = vec2<f32>(sin(uv.y * band + frame.time * 3.0) * k, 0.0);
    return sample(uv + off);
}
""", [p("range", "Range", 0, 100, 35), p("strength", "Strength", 0, 100, 35)], "Distort", intensity="strength"),

fx("jittered-ripples", "Jittered Ripples", 40, "Ripples that stutter and jump instead of flowing.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (4.0 + rate() * 6.0));
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let w = sin(r * 30.0 - t * 2.0) * 0.012;
    let q = uv + select(d / r, vec2<f32>(0.0), r < 1e-4) * w * frame.size.y / frame.size;
    return sample(q);
}
""", [SPEED], "Distort"),

fx("jittered-ripples-2", "Jittered Ripples 2", 41, "Horizontal bands of ripple that jump in steps.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (4.0 + rate() * 6.0));
    let off = vec2<f32>(sin(uv.y * 40.0 + t * 1.7) * 0.01 * (hash(vec2<f32>(t, 0.0), 1.0) + 0.3), 0.0);
    return sample(uv + off);
}
""", [SPEED], "Distort"),

fx("jittered-ripples-3", "Jittered Ripples 3", 42, "Criss-crossing ripples that twitch from frame to frame.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = floor(frame.time * (4.0 + rate() * 6.0));
    let off = vec2<f32>(sin(uv.y * 35.0 + t), sin(uv.x * 35.0 + t * 1.3)) * 0.008;
    let c = sample(uv + off);
    return vec4<f32>(c.rgb * (1.0 + off.x * 10.0), c.a);
}
""", [SPEED], "Distort"),

fx("vortex", "Vortex Setting", 43, "The picture twists into a vortex about its centre.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let a = params.strength / 100.0 * 4.0 * (1.0 - smoothstep(0.0, 0.6, r)) * (0.8 + 0.2 * sin(frame.time));
    let s = sin(a);
    let c = cos(a);
    let q = vec2<f32>(d.x * c - d.y * s, d.x * s + d.y * c) * frame.size.y / frame.size + vec2<f32>(0.5);
    return sample(q);
}
""", [p("strength", "Strength", 0, 100, 50)], "Distort", intensity="strength"),

fx("spinning-space", "Spinning Space", 44, "The picture repeats into a tunnel of itself that spins.", """
struct Params { size: f32, rotate: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = max(length(d), 1e-4);
    let a = atan2(d.y, d.x) + frame.time * params.rotate / 100.0 * 2.0;
    let depth = fract(log(r) * (1.0 + params.size / 100.0 * 2.0) - frame.time * 0.3);
    let q = vec2<f32>(fract(a / 6.2831853), depth);
    let c = sample(mirror_uv(q * 2.0));
    return vec4<f32>(c.rgb * smoothstep(0.0, 0.25, r), c.a);
}
""", [p("size", "Size", 0, 100, 34), p("rotate", "Spin", 0, 100, 67)], "Distort"),

fx("shockwave", "Shockwave", 45, "A shockwave bursts out from the centre, warping the picture as it passes.", """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate() * 0.5);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let front = ph * 1.2;
    let x = r - front;
    let ring = x * exp(-x * x / 0.004) * 8.0 * (1.0 - ph);
    let q = uv - select(d / r, vec2<f32>(0.0), r < 1e-4) * ring * 0.03 * frame.size.y / frame.size;
    let c = sample(q);
    return vec4<f32>(c.rgb * (1.0 + abs(ring) * 0.3), c.a);
}
""", [SPEED], "Distort"),

fx("striped-glass", "Striped Glass", 46, "The picture seen through ribbed glass, broken into offset stripes.", """
struct Params { size: f32, distortion: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let n = mix(8.0, 60.0, 1.0 - params.size / 100.0);
    let local = fract(uv.x * n) - 0.5;
    let q = vec2<f32>(uv.x + local * params.distortion / 100.0 * 0.6 / n * 4.0, uv.y);
    let c = sample(q);
    let shade = 1.0 - 0.15 * abs(local) * 2.0;
    return vec4<f32>(c.rgb * shade, c.a);
}
""", [p("size", "Size", 0, 100, 50), p("distortion", "Distortion", 0, 100, 100)], "Distort", intensity="distortion"),

fx("pool-reflection", "Pool Reflection", 47, "Rippling caustic light plays over the picture as at the bottom of a pool.", NOISE + """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let s = mix(3.0, 12.0, 1.0 - params.size / 100.0);
    let q = uv * vec2<f32>(frame.size.x / frame.size.y, 1.0) * s;
    let n1 = vnoise(q + vec2<f32>(t, t * 0.7));
    let n2 = vnoise(q * 1.3 - vec2<f32>(t * 0.8, -t * 0.5));
    let caustic = pow(1.0 - abs(n1 - n2) * 2.0, 6.0);
    let off = vec2<f32>(n1 - 0.5, n2 - 0.5) * 0.01;
    let c = sample(uv + off);
    let rgb = c.rgb * vec3<f32>(0.85, 1.0, 1.05) + vec3<f32>(0.6, 0.9, 1.0) * caustic * 0.4;
    return vec4<f32>(rgb, c.a);
}
""", [SPEED, p("size", "Size", 0, 100, 60)], "Distort"),

fx("distort", "Distort", 48, "The picture bends and wobbles out of shape.", NOISE + """
struct Params { speed: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = frame.time * rate();
    let q = uv * 3.0 + vec2<f32>(t * 0.5, t * 0.3);
    let off = (vec2<f32>(fbm(q), fbm(q + vec2<f32>(4.7, 1.9))) - vec2<f32>(0.5)) * 0.06;
    return sample(uv + off);
}
""", [SPEED], "Distort"),

fx("distorted-mirror", "Distorted", 49, "A funhouse-mirror bend that sways slowly.", """
struct Params { strength: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let k = params.strength / 100.0;
    let off = vec2<f32>(sin(uv.y * 6.0 + frame.time) * 0.03, sin(uv.x * 5.0 + frame.time * 0.8) * 0.02) * k;
    return sample(uv + off);
}
""", [p("strength", "Strength", 0, 100, 70)], "Distort", intensity="strength"),

fx("diamond-zoom", "Diamond Zoom", 50, "A diamond-shaped window zooms into the picture, turning as it grows.", """
struct Params { speed: f32, size: f32, rotate: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let t = 0.5 - 0.5 * cos(frame.time * rate() * 3.14159265);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let a = params.rotate / 100.0 * 0.8 * t;
    let s = sin(a);
    let c0 = cos(a);
    let r = vec2<f32>(d.x * c0 - d.y * s, d.x * s + d.y * c0);
    let diamond = abs(r.x) + abs(r.y);
    let size = mix(0.25, 0.7, params.size / 100.0);
    let zoom = 1.0 + t * 0.6;
    let inside = moved(uv, vec2<f32>(0.0), a, zoom);
    let c = sample(uv);
    let zc = sample(inside);
    let m = smoothstep(size, size - 0.01, diamond);
    let rim = exp(-abs(diamond - size) / 0.004) * 0.6;
    return vec4<f32>(mix(c.rgb * 0.6, zc.rgb, m) + vec3<f32>(rim), c.a);
}
""", [SPEED, p("size", "Size", 0, 100, 52), p("rotate", "Turn", 0, 100, 50)], "Distort"),

fx("chromo-zoom", "Chromo-zoom", 51, "The picture zooms in pulses with its colours pulled apart.", """
struct Params { speed: f32, size: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let ph = fract(frame.time * rate());
    let k = exp(-ph * 4.0) * (0.3 + params.size / 100.0);
    let r = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + k * 0.12));
    let g = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + k * 0.08));
    let b = sample(moved(uv, vec2<f32>(0.0), 0.0, 1.0 + k * 0.04));
    return vec4<f32>(r.r, g.g, b.b, g.a);
}
""", [SPEED, p("size", "Strength", 0, 100, 33)], "Distort", intensity="size"),

]
