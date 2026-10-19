fn inb(uv: vec2<f32>) -> bool {
    return uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0;
}

struct Params { pinch: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let s = max(1.0 - p, 0.0001);
    let c = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(c);
    let bend = 1.0 + p * params.pinch / 100.0 * 2.0;
    let rr = pow(r / s, bend) * s;
    let dir = select(c / r, vec2<f32>(0.0), r < 1e-5);
    let q = (dir * rr / s) * frame.size.y / frame.size + vec2<f32>(0.5);
    let z = 1.0 + 0.1 * (1.0 - p);
    let b = to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
    if (inb(q) && p < 0.999) {
        return mix(from_at(q), b, smoothstep(0.8, 1.0, p));
    }
    return b;
}
