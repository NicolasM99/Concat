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

fn split(uv: vec2<f32>, o: vec2<f32>) -> vec4<f32> {
    let g = sample(uv);
    return vec4<f32>(sample(uv + o).r, g.g, sample(uv - o).b, g.a);
}

fn scanlines(uv: vec2<f32>, amount: f32) -> f32 {
    return 1.0 - amount * step(0.5, fract(uv.y * frame.size.y / 3.0));
}

fn static_at(uv: vec2<f32>, t: f32) -> f32 {
    return hash(floor(uv * frame.size / 2.0), fract(t * 0.137) * 1000.0);
}

struct Params { distortion: f32, chroma_x: f32 }

fn effect(uv: vec2<f32>) -> vec4<f32> {
    let aspect = frame.size.x / frame.size.y;
    let d = (uv - vec2<f32>(0.5)) * vec2<f32>(aspect, 1.0);
    let k = params.distortion / 100.0 * 0.6;
    let q = d / (1.0 + k * dot(d, d)) * (1.0 + k * 0.3) / vec2<f32>(aspect, 1.0) + vec2<f32>(0.5);
    let c = split(q, vec2<f32>(params.chroma_x / 100.0 * 0.006, 0.0) * length(d) * 2.0);
    let rgb = s_curve(saturation(c.rgb, 1.15), 0.4);
    let vig = 1.0 - smoothstep(0.5, 0.9, length(d)) * 0.7;
    return vec4<f32>(rgb * vig, c.a);
}
