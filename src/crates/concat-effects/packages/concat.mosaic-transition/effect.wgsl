struct Params { size: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let e = sin(3.14159265 * progress);
    let px = max(1.0, e * params.size / 100.0 * frame.size.x / 8.0);
    let cell = frame.size / px;
    let q = (floor(uv * cell) + vec2<f32>(0.5)) / cell;
    let quv = select(q, uv, px <= 1.0);
    return mix(from_at(quv), to_at(quv), smoothstep(0.4, 0.6, progress));
}
