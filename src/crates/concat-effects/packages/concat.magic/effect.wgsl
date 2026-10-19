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

fn mirror_uv(uv: vec2<f32>) -> vec2<f32> {
    let m = abs(fract(uv * 0.5) * 2.0 - vec2<f32>(1.0));
    return vec2<f32>(1.0) - m;
}

fn moved(uv: vec2<f32>, offset: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return mirror_uv(r / frame.size + vec2<f32>(0.5) - offset);
}

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

fn rainbow(h: f32) -> vec3<f32> {
    let c = vec3<f32>(0.5) + 0.5 * cos(6.2831853 * (vec3<f32>(h) + vec3<f32>(0.0, 0.33, 0.67)));
    return c * c;
}

fn turn_hue(rgb: vec3<f32>, degrees: f32) -> vec3<f32> {
    let y = dot(rgb, vec3<f32>(0.299, 0.587, 0.114));
    let i = dot(rgb, vec3<f32>(0.596, -0.274, -0.322));
    let q = dot(rgb, vec3<f32>(0.211, -0.523, 0.312));
    let a = radians(degrees);
    let i2 = i * cos(a) - q * sin(a);
    let q2 = i * sin(a) + q * cos(a);
    return vec3<f32>(y + 0.956 * i2 + 0.621 * q2, y - 0.272 * i2 - 0.647 * q2, y - 1.106 * i2 + 1.703 * q2);
}

fn glint(d: vec2<f32>, size: f32) -> f32 {
    let a = abs(d) / max(size, 1e-4);
    let star = max(0.0, 1.0 - (a.x * 8.0 + a.y)) + max(0.0, 1.0 - (a.y * 8.0 + a.x));
    let core = exp(-dot(a, a) * 40.0);
    return star * 0.6 + core;
}

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
