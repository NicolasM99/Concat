struct Params { spin: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let p = smoothstep(0.0, 1.0, progress);
    let quarter = vec2<f32>(select(-1.0, 1.0, uv.x >= 0.5), select(-1.0, 1.0, uv.y >= 0.5));
    let q = uv - quarter * p * 0.5;
    let inside = (q.x - 0.5) * quarter.x >= 0.0 && (q.y - 0.5) * quarter.y >= 0.0 && q.x >= 0.0 && q.x <= 1.0 && q.y >= 0.0 && q.y <= 1.0;
    if (inside) {
        return from_at(q);
    }
    let z = 1.0 + 0.2 * (1.0 - p) * params.spin / 100.0;
    return to_at((uv - vec2<f32>(0.5)) / z + vec2<f32>(0.5));
}
