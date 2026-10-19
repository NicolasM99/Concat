"""WGSL snippets shared by the specs; each package carries its own copy."""

INB = """
fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}
"""

# Turn `uv` about `centre` by `angle`, in pixels so the turn is rigid.
ROT = """
fn rot_uv(uv: vec2<f32>, centre: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - centre) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return r / frame.size + centre;
}
"""

# Mirror a coordinate back into the frame, so a moved picture has no edge.
MIRROR = """
fn mirror_uv(uv: vec2<f32>) -> vec2<f32> {
    let m = abs(fract(uv * 0.5) * 2.0 - vec2<f32>(1.0));
    return vec2<f32>(1.0) - m;
}
"""

# Value noise and its fractal sum, 0..1, from the prelude's hash.
NOISE = """
fn vnoise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let u = f * f * (3.0 - 2.0 * f);
    let a = hash(i, 1.0);
    let b = hash(i + vec2<f32>(1.0, 0.0), 1.0);
    let c = hash(i + vec2<f32>(0.0, 1.0), 1.0);
    let d = hash(i + vec2<f32>(1.0, 1.0), 1.0);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

fn fbm(p: vec2<f32>) -> f32 {
    var sum = 0.0;
    var amp = 0.5;
    var q = p;
    for (var i = 0; i < 5; i++) {
        sum += amp * vnoise(q);
        q = q * 2.03 + vec2<f32>(17.1, 9.2);
        amp *= 0.5;
    }
    return sum / 0.96875;
}
"""

# A colour wheel, 0..1 around it, as light.
RAINBOW = """
fn rainbow(h: f32) -> vec3<f32> {
    let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67)));
    return c * c;
}
"""

# Either picture of a cut, blurred along `dir` (uv units) with nine taps.
DIRBLUR = """
fn blur_from(uv: vec2<f32>, dir: vec2<f32>) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += from_at(uv + dir * (f32(i) / 4.0));
    }
    return sum / 9.0;
}

fn blur_to(uv: vec2<f32>, dir: vec2<f32>) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += to_at(uv + dir * (f32(i) / 4.0));
    }
    return sum / 9.0;
}
"""

# Either picture blurred in a disc of `r` (uv of the height), twelve taps.
DISCBLUR = """
fn disc_from(uv: vec2<f32>, r: f32) -> vec4<f32> {
    var sum = from_at(uv);
    let aspect = frame.size.y / frame.size.x;
    for (var i = 0; i < 12; i++) {
        let a = f32(i) * 0.5235988;
        let k = select(1.0, 0.5, i % 2 == 1);
        sum += from_at(uv + vec2<f32>(cos(a) * aspect, sin(a)) * r * k);
    }
    return sum / 13.0;
}

fn disc_to(uv: vec2<f32>, r: f32) -> vec4<f32> {
    var sum = to_at(uv);
    let aspect = frame.size.y / frame.size.x;
    for (var i = 0; i < 12; i++) {
        let a = f32(i) * 0.5235988;
        let k = select(1.0, 0.5, i % 2 == 1);
        sum += to_at(uv + vec2<f32>(cos(a) * aspect, sin(a)) * r * k);
    }
    return sum / 13.0;
}
"""

# A heart, point down, about a unit tall about the origin, `q` with y up:
# negative inside (Inigo Quilez's distance).
HEART = """
fn heart_sdf(q: vec2<f32>) -> f32 {
    let p = vec2<f32>(abs(q.x), q.y + 0.55);
    if (p.y + p.x > 1.0) {
        return sqrt(dot(p - vec2<f32>(0.25, 0.75), p - vec2<f32>(0.25, 0.75))) - 0.35355;
    }
    let a = dot(p - vec2<f32>(0.0, 1.0), p - vec2<f32>(0.0, 1.0));
    let t = max(p.x + p.y, 0.0) * 0.5;
    let b = dot(p - vec2<f32>(t), p - vec2<f32>(t));
    return sqrt(min(a, b)) * sign(p.x - p.y);
}
"""

# A four-pointed glint at `d` from its centre, `size` across.
GLINT = """
fn glint(d: vec2<f32>, size: f32) -> f32 {
    let a = abs(d) / max(size, 1e-4);
    let star = max(0.0, 1.0 - (a.x * 8.0 + a.y)) + max(0.0, 1.0 - (a.y * 8.0 + a.x));
    let core = exp(-dot(a, a) * 40.0);
    return star * 0.6 + core;
}
"""

def p(key, label, mn, mx, default, step=1, unit="%", values=None, labels=None):
    d = {"key": key, "label": label, "min": mn, "max": mx, "default": default, "step": step}
    if unit:
        d["unit"] = unit
    if values is not None:
        d = {"key": key, "label": label, "min": values[0], "max": values[-1], "default": default,
             "step": 1, "values": values, "labels": labels}
    return d

def T(slug, name, category, order, description, wgsl, params=(), **kw):
    d = {"slug": slug, "name": name, "kind": "transition", "category": category, "order": order,
         "description": description, "wgsl": wgsl, "params": list(params)}
    d.update(kw)
    return d

def E(slug, name, category, order, description, wgsl, params=(), **kw):
    d = {"slug": slug, "name": name, "kind": "effect", "category": category, "order": order,
         "description": description, "wgsl": wgsl, "params": list(params)}
    d.update(kw)
    return d

# Every hue turned by `degrees` about luminance, brightness held: a turn in
# the YIQ plane, usable in any space (the prelude's `hue_rotate` is the
# display library's alone).
HUE = """
fn turn_hue(rgb: vec3<f32>, degrees: f32) -> vec3<f32> {
    let y = dot(rgb, vec3<f32>(0.299, 0.587, 0.114));
    let i = dot(rgb, vec3<f32>(0.596, -0.274, -0.322));
    let q = dot(rgb, vec3<f32>(0.211, -0.523, 0.312));
    let a = radians(degrees);
    let i2 = i * cos(a) - q * sin(a);
    let q2 = i * sin(a) + q * cos(a);
    return vec3<f32>(y + 0.956 * i2 + 0.621 * q2, y - 0.272 * i2 - 0.647 * q2, y - 1.106 * i2 + 1.703 * q2);
}
"""
