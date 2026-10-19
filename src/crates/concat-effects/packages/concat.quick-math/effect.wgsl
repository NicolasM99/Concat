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

fn glint(d: vec2<f32>, size: f32) -> f32 {
    let a = abs(d) / max(size, 1e-4);
    let star = max(0.0, 1.0 - (a.x * 8.0 + a.y)) + max(0.0, 1.0 - (a.y * 8.0 + a.x));
    let core = exp(-dot(a, a) * 40.0);
    return star * 0.6 + core;
}

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
