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
