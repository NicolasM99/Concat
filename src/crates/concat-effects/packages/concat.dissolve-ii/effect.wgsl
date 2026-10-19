struct Params { grain: f32 }

fn transition(uv: vec2<f32>, progress: f32) -> vec4<f32> {
    let cell = max(params.grain, 1.0);
    let n = hash(floor(uv * frame.size / cell), 7.0);
    let m = smoothstep(n - 0.04, n + 0.04, progress * 1.08 - 0.04);
    return mix(from_at(uv), to_at(uv), m);
}
