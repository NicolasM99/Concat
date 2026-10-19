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

fn line_blur(uv: vec2<f32>, d: vec2<f32>) -> vec4<f32> {
    var sum = vec4<f32>(0.0);
    for (var i = -4; i <= 4; i++) {
        sum += sample_premultiplied(uv + d * (f32(i) / 4.0));
    }
    let m = sum / 9.0;
    return vec4<f32>(m.rgb / max(m.a, 1e-4), m.a);
}

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
