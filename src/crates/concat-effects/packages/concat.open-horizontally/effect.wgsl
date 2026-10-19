struct Params { gap: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let half = p * 0.5;
    if (uv.x < 0.5 - half) {
        return from_at(vec2<f32>(uv.x + half, uv.y));
    }
    if (uv.x > 0.5 + half) {
        return from_at(vec2<f32>(uv.x - half, uv.y));
    }
    let z = 1.0 + 0.15 * (1.0 - p) * params.gap / 100.0;
    let b = to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
    let shade = 1.0 - 0.5 * (1.0 - p) * params.gap / 100.0;
    return vec4<f32>(b.rgb * shade, b.a);
}
