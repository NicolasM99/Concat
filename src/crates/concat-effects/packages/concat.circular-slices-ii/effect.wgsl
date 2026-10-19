fn rot_uv(uv: vec2<f32>, centre: vec2<f32>, angle: f32, scale: f32) -> vec2<f32> {
    let c = (uv - centre) * frame.size;
    let s = sin(angle);
    let co = cos(angle);
    let r = vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / max(scale, 0.0001);
    return r / frame.size + centre;
}

struct Params { rings: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let n = max(params.rings, 2.0);
    let d = (uv - vec2<f32>(0.5)) * frame.size / frame.size.y;
    let r = length(d);
    let ring = floor(r * n * 1.2);
    let delay = min(ring / (n * 1.2), 1.0) * 0.5;
    let t = smoothstep(0.0, 1.0, clamp((progress - delay) / 0.5, 0.0, 1.0));
    let side = select(-1.0, 1.0, fract(ring * 0.5) < 0.25);
    let spin = sin(3.14159265 * t) * 0.8 * side;
    let q = rot_uv(uv, vec2<f32>(0.5), spin, 1.0);
    return select(from_at(q), to_at(q), t >= 0.5);
}
