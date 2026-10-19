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
