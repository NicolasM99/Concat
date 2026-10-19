struct Params { twist: f32 }

fn swirl_uv(uv: vec2<f32>, amount: f32) -> vec2<f32> {
    let c = (uv - vec2<f32>(0.5)) * frame.size;
    let d = length(c) / frame.size.y;
    let a = amount * (1.0 - smoothstep(0.0, 0.7, d));
    let s = sin(a);
    let co = cos(a);
    return vec2<f32>(c.x * co - c.y * s, c.x * s + c.y * co) / frame.size + vec2<f32>(0.5);
}

// The swirl of Swirl, turning the other way round.
fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let k = -sin(p * 3.14159265) * params.twist * 0.06;
    let a = from_at(swirl_uv(uv, k));
    let b = to_at(swirl_uv(uv, -k));
    return mix(a, b, p);
}
